from __future__ import annotations

import json
import math
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


BJT = ZoneInfo("Asia/Shanghai")
NOW = datetime.now(BJT)
PROJECT = Path(r"D:\codex\技能项目\crypto_macro_daily")
OUT_ROOT = Path(r"D:\codex\crypto_macro_daily")
OUT_ROOT.mkdir(parents=True, exist_ok=True)
DATA_PATH = PROJECT / "live_market_detail_20261013.json"
SUPPLEMENT_PATH = PROJECT / "research_supplement_20261013_0811.json"
VIEWS_PATH = PROJECT / "verified_updates_20261013_0811.json"
WHALE_PATH = PROJECT / "whale_treasury_orderflow_20261011_latest.json"
D = json.loads(DATA_PATH.read_text(encoding="utf-8"))
S = json.loads(SUPPLEMENT_PATH.read_text(encoding="utf-8"))
V = json.loads(VIEWS_PATH.read_text(encoding="utf-8"))
if WHALE_PATH.exists():
    D["whale_treasury_orderflow"] = json.loads(WHALE_PATH.read_text(encoding="utf-8"))
TAG = "2026-10-13_0811BJT"
OUT = OUT_ROOT / f"crypto_macro_daily_{TAG}.docx"
ASSET_DIR = OUT_ROOT / f"_assets_{TAG}"
ASSET_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, r"D:\codex\skills\crypto-macro-daily-review\scripts")
from snapshot_planner import classify_htf, execution_state
from turning_point_overlay import analyze as analyze_turning_points


BLUE = "1F4E78"
LIGHT_BLUE = "EAF2F8"
LIGHT_GREEN = "E8F5E9"
LIGHT_RED = "FCE8E6"
GREY = "F2F4F5"
TEXT = RGBColor(25, 33, 42)


def profile(asset: str) -> dict:
    candles = D["derivatives"][asset]["klines"][:-1]
    typical = [(float(x[2]) + float(x[3]) + float(x[4])) / 3 for x in candles]
    low, high = min(typical), max(typical)
    width = (high - low) / 50
    bins = defaultdict(float)
    for candle, price in zip(candles, typical):
        bins[min(49, int((price - low) / width))] += float(candle[5]) * price
    poc_i = max(bins, key=bins.get)
    selected = {poc_i}
    included = bins[poc_i]
    total = sum(bins.values())
    left, right = poc_i - 1, poc_i + 1
    while included < total * 0.70:
        if right < 50 and (left < 0 or bins.get(right, 0) >= bins.get(left, 0)):
            selected.add(right)
            included += bins.get(right, 0)
            right += 1
        else:
            selected.add(left)
            included += bins.get(left, 0)
            left -= 1
    return {
        "low": low,
        "high": high,
        "width": width,
        "bins": bins,
        "poc": low + (poc_i + 0.5) * width,
        "val": low + min(selected) * width,
        "vah": low + (max(selected) + 1) * width,
        "coverage": included / total,
    }


P = {asset: profile(asset) for asset in ("BTC", "ETH", "SOL", "UNI", "AVAX", "XRP")}
# The selected altcoin pair is not in the derivatives payload used for the
# core dashboard, so keep its independently fetched 5-day profile explicit.
ALT_PROFILES = {
    "AVAX": P["AVAX"],
    "XRP": P["XRP"],
}


def daily_trend(asset: str) -> dict:
    closes = [float(x[4]) for x in D["derivatives"][asset]["klines1d"][:-1]]
    last = closes[-1]
    ma20 = sum(closes[-20:]) / 20
    ma60 = sum(closes[-60:]) / 60
    ma20_prev = sum(closes[-25:-5]) / 20
    ma60_prev = sum(closes[-65:-5]) / 60
    if last > ma20 > ma60 and ma20 > ma20_prev and ma60 >= ma60_prev:
        label = "中线偏多"
    elif last < ma20 < ma60 and ma20 < ma20_prev and ma60 <= ma60_prev:
        label = "中线偏空"
    else:
        label = "中线震荡"
    return {"label": label, "last": last, "ma20": ma20, "ma60": ma60}


TRENDS = {asset: daily_trend(asset) for asset in ("BTC", "ETH", "SOL")}
REGIMES = {}
for asset in ("BTC", "ETH", "SOL"):
    htf, confidence, details = classify_htf(D["derivatives"][asset]["klines4h"][:-1])
    REGIMES[asset] = {
        "htf": htf,
        "confidence": confidence,
        "execution": execution_state(D["derivatives"][asset]["klines"][:-1], htf),
        "details": details,
    }

TURNING = analyze_turning_points(D["derivatives"]["BTC"]["klines4h"][:-1])


def net_rr(entry: float, stop: float, target: float, side: str, cost_rate: float = 0.0012) -> float:
    cost = entry * cost_rate
    risk = abs(entry - stop) + cost
    gross_reward = target - entry if side == "long" else entry - target
    return (gross_reward - cost) / risk


BTC_VAL = P["BTC"]["val"]
BTC_POC = P["BTC"]["poc"]
BTC_VAH = P["BTC"]["vah"]
BTC_LOW24 = D["derivatives"]["BTC"]["low24"]
LONG_ENTRY_LO, LONG_IDEAL, LONG_MAX = BTC_VAL - 100.0, BTC_VAL - 20.0, BTC_VAL + 50.0
LONG_STOP, LONG_TP1, LONG_TP2 = BTC_VAL - 500.0, BTC_POC, BTC_VAH
SHORT_ENTRY_LO, SHORT_IDEAL, SHORT_MAX = BTC_VAH - 100.0, BTC_VAH + 20.0, BTC_VAH + 80.0
SHORT_STOP, SHORT_TP1, SHORT_TP2 = BTC_VAH + 500.0, BTC_POC, BTC_VAL
LONG_RR1 = net_rr(LONG_MAX, LONG_STOP, LONG_TP1, "long")
LONG_RR2 = net_rr(LONG_MAX, LONG_STOP, LONG_TP2, "long")
LONG_WEIGHTED_RR = 0.4 * LONG_RR1 + 0.6 * LONG_RR2
SHORT_RR1 = net_rr(SHORT_MAX, SHORT_STOP, SHORT_TP1, "short")
SHORT_RR2 = net_rr(SHORT_MAX, SHORT_STOP, SHORT_TP2, "short")
SHORT_WEIGHTED_RR = 0.4 * SHORT_RR1 + 0.6 * SHORT_RR2
LONG_VALID = LONG_RR1 >= 1.0 and LONG_WEIGHTED_RR >= 1.3
LONG_STATUS_TEXT = "下沿扫低收回后做多" if LONG_VALID else "INVALID：POC过近，TP1净R:R不足，不做多"
STOP_DISTANCE = (LONG_MAX - LONG_STOP) / LONG_MAX
NOTIONAL_EQUITY = 0.001 / STOP_DISTANCE


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def prevent_row_split(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    cant_split = OxmlElement("w:cantSplit")
    tr_pr.append(cant_split)


def shade(cell, fill: str) -> None:
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    cell._tc.get_or_add_tcPr().append(shd)


def configure_run(run, size=9.2, bold=False, color=None) -> None:
    run.font.name = "Microsoft YaHei"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    run.font.size = Pt(size)
    run.bold = bold
    run.font.color.rgb = color or TEXT


def paragraph(doc, text: str, size=9.6, bold=False, after=4, align=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.12
    if align is not None:
        p.alignment = align
    configure_run(p.add_run(text), size=size, bold=bold)
    return p


def heading(doc, text: str, level=1):
    p = doc.add_heading(text, level=level)
    p.paragraph_format.space_before = Pt(9 if level == 1 else 6)
    p.paragraph_format.space_after = Pt(3)
    for run in p.runs:
        configure_run(run, size=15 if level == 1 else 11.2, bold=True, color=RGBColor(31, 78, 121))
    return p


def table(doc, headers, rows, font=7.5, first_col_bold=False):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = True
    set_repeat_table_header(t.rows[0])
    for index, header in enumerate(headers):
        cell = t.rows[0].cells[index]
        cell.text = str(header)
        shade(cell, BLUE)
        for run in cell.paragraphs[0].runs:
            configure_run(run, font, True, RGBColor(255, 255, 255))
    for row_index, row in enumerate(rows):
        cells = t.add_row().cells
        prevent_row_split(t.rows[-1])
        for index, value in enumerate(row):
            cell = cells[index]
            cell.text = str(value)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            if row_index % 2:
                shade(cell, LIGHT_BLUE)
            for p in cell.paragraphs:
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.0
                for run in p.runs:
                    configure_run(run, font, first_col_bold and index == 0)
    paragraph(doc, "", size=2, after=1)
    return t


def add_picture(doc, path: Path, caption: str):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(path), width=Inches(6.9))
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c.paragraph_format.space_after = Pt(5)
    configure_run(c.add_run(caption), size=8.0, color=RGBColor(70, 70, 70))


def chart_price_levels() -> Path:
    path = ASSET_DIR / "price_levels.png"
    fig, axes = plt.subplots(3, 1, figsize=(10, 8.3), constrained_layout=True)
    colors = {"BTC": "#1f4e79", "ETH": "#6f2da8", "SOL": "#138a4b"}
    for ax, asset in zip(axes, ("BTC", "ETH", "SOL")):
        closes = [float(x[4]) for x in D["derivatives"][asset]["klines"][-73:-1]]
        x = list(range(len(closes)))
        p = P[asset]
        ax.plot(x, closes, color=colors[asset], lw=1.8, label="1h close")
        ax.axhspan(p["val"], p["vah"], color="#dbeaf5", alpha=0.75, label="VA: normal 70% volume range")
        ax.axhline(p["val"], color="#2f75b5", ls="--", lw=1.0, label="VAL: normal range low")
        ax.axhline(p["poc"], color="#ed7d31", lw=1.2, label="POC: busiest price")
        ax.axhline(p["vah"], color="#2f75b5", ls="-.", lw=1.0, label="VAH: normal range high")
        ax.scatter([len(closes) - 1], [D["derivatives"][asset]["mark"]], s=28, color=colors[asset], zorder=5)
        ax.set_title(f"{asset}: last 72 completed 1h closes and estimated 5-day value area", fontsize=10, weight="bold")
        ax.grid(alpha=0.22)
        ax.tick_params(labelsize=8)
        if asset == "BTC":
            ax.legend(loc="upper left", ncol=2, fontsize=7)
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path


def chart_etf() -> Path:
    path = ASSET_DIR / "etf_flows.png"
    rows = S["etf_flows_usd_m"]
    labels = [row["date"][5:] for row in rows]
    x = range(len(rows))
    width = 0.24
    fig, ax = plt.subplots(figsize=(9.6, 4.4), constrained_layout=True)
    for offset, asset, color in ((-width, "BTC", "#1f4e79"), (0, "ETH", "#6f2da8"), (width, "SOL", "#138a4b")):
        ax.bar([i + offset for i in x], [row[asset] if row[asset] is not None else float("nan") for row in rows], width=width, label=asset, color=color)
    ax.axhline(0, color="#555", lw=0.8)
    ax.set_xticks(list(x), labels)
    ax.set_ylabel("US$m")
    ax.set_title("US spot ETF daily net flow: final/latest published values", weight="bold")
    ax.legend(ncol=3)
    ax.grid(axis="y", alpha=0.22)
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path


def chart_derivatives() -> Path:
    path = ASSET_DIR / "derivatives.png"
    fig, axes = plt.subplots(2, 2, figsize=(10, 7.1), constrained_layout=True)
    assets = ("BTC", "ETH", "SOL")
    colors = {"BTC": "#1f4e79", "ETH": "#6f2da8", "SOL": "#138a4b"}
    for asset in assets:
        values = [row["value"] / 1e9 for row in D["derivatives"][asset]["oi_5d"]]
        axes[0, 0].plot(range(len(values)), values, marker="o", ms=3.5, label=asset, color=colors[asset])
    axes[0, 0].set_title("OI notional: latest six daily observations", weight="bold")
    axes[0, 0].set_ylabel("US$bn")
    axes[0, 0].set_xticks(range(6), ["D-5", "D-4", "D-3", "D-2", "D-1", "Now"])
    axes[0, 0].legend(ncol=3, fontsize=8)
    axes[0, 0].grid(alpha=0.22)
    axes[0, 1].bar(assets, [D["derivatives"][a]["oi24_pct"] for a in assets], color=[colors[a] for a in assets])
    axes[0, 1].axhline(0, color="#555", lw=0.8)
    axes[0, 1].set_title("OI notional 24h change", weight="bold")
    axes[0, 1].set_ylabel("%")
    axes[0, 1].grid(axis="y", alpha=0.22)
    axes[1, 0].bar(assets, [D["derivatives"][a]["funding"] for a in assets], color=[colors[a] for a in assets])
    axes[1, 0].axhline(0, color="#555", lw=0.8)
    axes[1, 0].set_title("Latest funding rate", weight="bold")
    axes[1, 0].set_ylabel("% per funding interval")
    axes[1, 0].grid(axis="y", alpha=0.22)
    for asset in assets:
        axes[1, 1].plot((1, 2, 3), D["derivatives"][asset]["taker_last3"], marker="o", label=asset, color=colors[asset])
    axes[1, 1].axhline(1.0, color="#555", ls="--", lw=0.9)
    axes[1, 1].set_xticks((1, 2, 3), ("T-2", "T-1", "Latest"))
    axes[1, 1].set_title("Taker buy/sell imbalance proxy: last 3h", weight="bold")
    axes[1, 1].legend(ncol=3, fontsize=8)
    axes[1, 1].grid(alpha=0.22)
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path


def chart_profile_liquidity() -> Path:
    path = ASSET_DIR / "profile_liquidity.png"
    fig, axes = plt.subplots(3, 2, figsize=(10, 9.2), constrained_layout=True)
    proxy = {
        "BTC": {"down": [P["BTC"]["val"], D["derivatives"]["BTC"]["low24"], max(P["BTC"]["low"], D["derivatives"]["BTC"]["low24"] - 0.35 * (P["BTC"]["high"] - P["BTC"]["low"]))], "up": [P["BTC"]["vah"], min(P["BTC"]["high"], P["BTC"]["vah"] + 0.18 * (P["BTC"]["high"] - P["BTC"]["low"])), P["BTC"]["high"]]},
        "ETH": {"down": [P["ETH"]["val"], D["derivatives"]["ETH"]["low24"], max(P["ETH"]["low"], D["derivatives"]["ETH"]["low24"] - 0.35 * (P["ETH"]["high"] - P["ETH"]["low"]))], "up": [P["ETH"]["vah"], min(P["ETH"]["high"], P["ETH"]["vah"] + 0.18 * (P["ETH"]["high"] - P["ETH"]["low"])), P["ETH"]["high"]]},
        "SOL": {"down": [P["SOL"]["val"], D["derivatives"]["SOL"]["low24"], max(P["SOL"]["low"], D["derivatives"]["SOL"]["low24"] - 0.35 * (P["SOL"]["high"] - P["SOL"]["low"]))], "up": [P["SOL"]["vah"], min(P["SOL"]["high"], P["SOL"]["vah"] + 0.18 * (P["SOL"]["high"] - P["SOL"]["low"])), P["SOL"]["high"]]},
    }
    for row, asset in enumerate(("BTC", "ETH", "SOL")):
        p = P[asset]
        centers = [p["low"] + (i + 0.5) * p["width"] for i in range(50)]
        volumes = [p["bins"].get(i, 0) / 1e6 for i in range(50)]
        ax = axes[row, 0]
        ax.barh(centers, volumes, height=p["width"] * 0.9, color="#9dc3e6")
        ax.axhspan(p["val"], p["vah"], color="#d9ead3", alpha=0.48)
        ax.axhline(p["poc"], color="#ed7d31", lw=1.4)
        ax.axhline(D["derivatives"][asset]["mark"], color="#1f1f1f", lw=1.0, ls="--")
        ax.set_title(f"{asset} estimated volume profile", fontsize=9, weight="bold")
        ax.set_xlabel("Quote volume, US$m")
        ax.grid(axis="x", alpha=0.2)
        ax.tick_params(labelsize=7.5)
        ax2 = axes[row, 1]
        mark = D["derivatives"][asset]["mark"]
        down_levels = sorted(proxy[asset]["down"])
        up_levels = sorted(proxy[asset]["up"])
        levels = down_levels + [mark] + up_levels
        colors = ["#2f75b5"] * len(down_levels) + ["#222"] + ["#c00000"] * len(up_levels)
        ax2.scatter([0.5] * len(levels), levels, c=colors, s=45, zorder=3)

        # Place labels in fixed lanes and connect them to price points. This keeps
        # tightly clustered levels legible without letting text collide or escape.
        label_lanes = (
            (down_levels, "downside long-stop proxy", 0.04, (0.08, 0.18, 0.28), "#2f75b5"),
            (up_levels, "upside short-stop proxy", 0.60, (0.60, 0.76, 0.91), "#c00000"),
        )
        for group, label, x_text, y_slots, color in label_lanes:
            for level, y_text in zip(group, y_slots):
                ax2.annotate(
                    f"{level:,.2f}\n{label}",
                    xy=(0.5, level),
                    xycoords="data",
                    xytext=(x_text, y_text),
                    textcoords=ax2.transAxes,
                    ha="left",
                    va="center",
                    fontsize=6.5,
                    color=color,
                    arrowprops={"arrowstyle": "-", "color": color, "lw": 0.5},
                )
        ax2.annotate(
            f"{mark:,.2f}\ncurrent",
            xy=(0.5, mark),
            xycoords="data",
            xytext=(0.36, 0.44),
            textcoords=ax2.transAxes,
            ha="right",
            va="center",
            fontsize=7,
            color="#222",
            arrowprops={"arrowstyle": "-", "color": "#222", "lw": 0.5},
        )
        ax2.set_xlim(0, 1)
        ax2.set_xticks([])
        ax2.set_title(f"{asset} inferred two-sided stop zones", fontsize=9, weight="bold")
        ax2.grid(axis="y", alpha=0.2)
        ax2.tick_params(labelsize=7.5)
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path


def chart_alt_alpha() -> Path:
    path = ASSET_DIR / "alt_alpha.png"
    btc_change = D["derivatives"]["BTC"]["change24"]
    assets = ("AVAX", "XRP")
    relative = [S["alt_snapshot"][a]["change24_pct"] - btc_change for a in assets]
    activity_change = [S["alt_fundamentals"]["AVAX"]["dex_volume_7d_pct"], float("nan")]
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.2), constrained_layout=True)
    axes[0].bar(assets, relative, color=["#e67e22", "#138a4b"])
    axes[0].axhline(0, color="#555", lw=0.8)
    axes[0].set_title("24h relative return vs BTC", weight="bold")
    axes[0].set_ylabel("percentage points")
    axes[0].grid(axis="y", alpha=0.22)
    axes[1].bar(assets, activity_change, color=["#e67e22", "#138a4b"])
    axes[1].axhline(0, color="#555", lw=0.8)
    axes[1].set_title("Verified 7-day DEX volume change", weight="bold")
    axes[1].set_ylabel("%")
    axes[1].grid(axis="y", alpha=0.22)
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path


CHARTS = {
    "levels": chart_price_levels(),
    "etf": chart_etf(),
    "derivatives": chart_derivatives(),
    "profile": chart_profile_liquidity(),
    "alt": chart_alt_alpha(),
}


def make_document() -> Path:
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.48)
    section.bottom_margin = Inches(0.35)
    section.left_margin = Inches(0.55)
    section.right_margin = Inches(0.55)

    styles = doc.styles
    styles["Normal"].font.name = "Microsoft YaHei"
    styles["Normal"]._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    styles["Normal"].font.size = Pt(9.4)
    for level in range(1, 4):
        style = styles[f"Heading {level}"]
        style.font.name = "Microsoft YaHei"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_after = Pt(2)
    configure_run(title.add_run("加密宏观每日复盘"), size=21, bold=True, color=RGBColor(31, 78, 121))
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.paragraph_format.space_after = Pt(8)
    configure_run(subtitle.add_run(f"2026-10-13 | 市场快照 {D['retrieved_bjt'][11:16]} BJT | 规则：snapshot-regime-router-v1 + dynamic-rr-v1 + turning-point-overlay-shadow-v1"), size=8.4, color=RGBColor(90, 90, 90))

    heading(doc, "数据快照说明")
    paragraph(doc, f"本报告使用 {D['retrieved_bjt']} 的 Binance 同轮行情、衍生品、Deribit 期权、Binance/OKX 现货成交带与盘口快照；ETF BTC 最新公开值到 2026-10-07，ETH/SOL 当日值未完整取得，宏观、催化剂与大佬观点核验截止 {D['retrieved_bjt'][:10]} {D['retrieved_bjt'][11:16]} BJT。条件卡只在写明的有效期内成立，不代表全天自动监控。")

    heading(doc, "今日结论")
    btc_mark = D["derivatives"]["BTC"]["mark"]
    paragraph(doc, f"当前价 {btc_mark:,.0f} 位于 POC {BTC_POC:,.0f} 上方、接近价值区上半部，不直接追多或追空；今天下沿多头路径因 POC 过近、TP1 净R:R不足而 INVALID，不执行。唯一保留的条件路径是上方 {SHORT_ENTRY_LO:,.0f}-{SHORT_MAX:,.0f} 冲高受阻后做空。条件卡有效至 2026-10-13 20:00 BJT，或结构/事件先失效。", size=11.0, bold=True, after=6)
    heading(doc, "中线趋势与阶段交易", 3)
    table(doc, ["资产", "中线趋势", "当前阶段", "阶段交易优先级", "推翻条件"], [
        ["BTC", TRENDS["BTC"]["label"], "日线低于20D但高于60D / 4H区间 / 现价位于价值区中上部", f"下沿多头 INVALID（POC过近）；只保留上沿 {SHORT_ENTRY_LO:,.0f}-{SHORT_MAX:,.0f} 受阻做空", f"4H重新形成明确趋势，或有效脱离 {BTC_VAL:,.0f}-{BTC_VAH:,.0f} 价值区"],
        ["ETH", TRENDS["ETH"]["label"], "日线高于60D但低于20D / 4H过渡 / 现价接近VAL", f"观察 VAL {P['ETH']['val']:,.0f} 收回与 EMA20 {REGIMES['ETH']['details']['ema20']:,.0f}，无独立交易卡", f"4H重新站稳 EMA20 {REGIMES['ETH']['details']['ema20']:,.0f} 或跌破60D"],
        ["SOL", TRENDS["SOL"]["label"], "日线低于20D但高于60D / 4H过渡 / 现价接近VAL", f"只观察 VAL {P['SOL']['val']:,.2f} 附近的扫低收回，不给独立交易卡", f"4H 收回 EMA20 {REGIMES['SOL']['details']['ema20']:,.2f} 且日线重新站回20D"],
    ], font=7.1, first_col_bold=True)
    paragraph(doc, "三者日线都低于20日均线但仍高于60日均线，BTC的4H是区间，ETH/SOL处于过渡，因此当前更准确的描述是‘中线震荡、短线偏弱’，还不是确认的大级别牛市或熊市。今天下沿多头因第一阻力过近而取消，只保留上沿受阻空头条件。")

    heading(doc, "今日条件式交易预案", 3)
    table(doc, ["优先级", "品种/方向", "If-Then 触发", "Entry / Max", "SL", "TP1 / TP2", "净R:R", "到期/取消"], [
        ["1", "BTC 多（S1/S5）INVALID", f"下沿 {LONG_ENTRY_LO:,.0f}-{LONG_MAX:,.0f} 即使扫低收回也不执行：POC {BTC_POC:,.0f} 距离过近，TP1净R:R不足", f"{LONG_ENTRY_LO:,.0f}-{LONG_MAX:,.0f} / {LONG_MAX:,.0f}", f"{LONG_STOP:,.0f}", f"{LONG_TP1:,.0f} / {LONG_TP2:,.0f}", f"TP1 1:{LONG_RR1:.2f}；加权 1:{LONG_WEIGHTED_RR:.2f}", "本轮取消；等待价值区重算"],
        ["2", "BTC 空（S5上沿受阻回落）", f"若价格进入 {SHORT_ENTRY_LO:,.0f}-{SHORT_MAX:,.0f}，15m/30m出现冲高失败、LH并重新跌回 VAH {BTC_VAH:,.0f} 下方，且 Taker<0.90或OI继续增加而价格不再上行，则执行", f"{SHORT_ENTRY_LO:,.0f}-{SHORT_MAX:,.0f} / {SHORT_MAX:,.0f}", f"{SHORT_STOP:,.0f}", f"{SHORT_TP1:,.0f} / {SHORT_TP2:,.0f}", f"TP1 1:{SHORT_RR1:.2f}；加权 1:{SHORT_WEIGHTED_RR:.2f}", "2026-10-13 20:00；重新站稳Max Entry或价值区重算即取消"],
    ], font=6.2, first_col_bold=True)
    paragraph(doc, f"BTC 当前在 POC {BTC_POC:,.0f} 附近，POC 可以理解为最近成交最拥挤的中轴，不是追单位置。今天下沿多头卡因第一阻力过近被取消；只有上方 {SHORT_ENTRY_LO:,.0f}-{SHORT_MAX:,.0f} 冲高失败、跌回 VAH 下方并形成 LH，才考虑做空。每张有效卡最多0.10%账户风险，只是亏损上限，不是必须用满的目标仓位。", size=10.0, after=6)

    heading(doc, "阶段顶底雷达（Shadow）", 3)
    turning_rows = []
    for horizon in ("24h", "72h", "7d"):
        m = TURNING["horizons"][horizon]
        envelope = m.get("statistical_envelope", {}).get("one_sigma", [P["BTC"]["low"], P["BTC"]["high"]])
        low_band = m.get("conditional_low_band", [P["BTC"]["val"], P["BTC"]["poc"]])
        high_band = m.get("conditional_high_band", [P["BTC"]["poc"], P["BTC"]["vah"]])
        share = m.get("scenario_share", {"BOTTOM_REBOUND_FIRST": 0.0, "TOP_REVERSAL_FIRST": 0.0, "NO_DIRECTIONAL_TURN": 1.0})
        wash = m.get("diagnostic_share", {}).get("two_way_wash", 0.0)
        turning_rows.append([
            horizon,
            f"{envelope[0]:,.0f}-{envelope[1]:,.0f}",
            f"{low_band[0]:,.0f}-{low_band[-1]:,.0f}",
            f"{high_band[0]:,.0f}-{high_band[-1]:,.0f}",
            f"{share['BOTTOM_REBOUND_FIRST']*100:.1f}% / {share['TOP_REVERSAL_FIRST']*100:.1f}% / {share['NO_DIRECTIONAL_TURN']*100:.1f}%",
            f"{wash*100:.1f}%",
            f"{m.get('effective_n', 0.0):.1f}",
            "SHADOW_UNCALIBRATED",
        ])
    table(doc, ["窗口", "统计±1σ", "条件底带", "条件顶带", "历史近邻：底/顶/无", "双向洗盘", "有效N", "状态"], turning_rows, font=6.6)
    paragraph(doc, f"这不是胜率。当前统计带只用于说明波动范围，不能把某一个点位当成绝对顶部。今天更重要的是观察上沿 {SHORT_ENTRY_LO:,.0f}-{SHORT_MAX:,.0f} 是否冲高失败并形成LH；VAL {BTC_VAL:,.0f} 即使收回，也因POC过近而暂不构成多头交易条件。")

    heading(doc, "今日交易台")
    table(doc, ["标的", "Bias", "Location", "Regime", "交易含义"], [
        ["BTC", TRENDS["BTC"]["label"], f"VAL {P['BTC']['val']:,.0f} / POC {P['BTC']['poc']:,.0f} / VAH {P['BTC']['vah']:,.0f}", f"{REGIMES['BTC']['htf']} + {REGIMES['BTC']['execution']}", "区间中部不追单；下沿多 INVALID；只等上沿受阻空"],
        ["ETH", TRENDS["ETH"]["label"], f"VAL {P['ETH']['val']:,.0f} / POC {P['ETH']['poc']:,.0f} / VAH {P['ETH']['vah']:,.0f}", f"{REGIMES['ETH']['htf']} + {REGIMES['ETH']['execution']}", "过渡区，等待重新站回EMA20或跌破60D"],
        ["SOL", TRENDS["SOL"]["label"], f"VAL {P['SOL']['val']:,.2f} / POC {P['SOL']['poc']:,.2f} / VAH {P['SOL']['vah']:,.2f}", f"{REGIMES['SOL']['htf']} + {REGIMES['SOL']['execution']}", "4H过渡、接近VAL，不追空也不接多"],
        ["Alt breadth", "普遍反弹但未确认轮动", f"XRP {D['derivatives']['XRP']['change24']:+.2f}%；DOGE {D['derivatives']['DOGE']['change24']:+.2f}%；AVAX {D['derivatives']['AVAX']['change24']:+.2f}%", "Relief bounce", "S4不执行，只保留研究"],
    ], font=7.2)
    paragraph(doc, f"POC {BTC_POC:,.0f} 是最近五天成交最密集的价格，可理解为短期筹码最拥挤的‘价格磁铁’；VAL {BTC_VAL:,.0f} 是正常震荡区下沿，VAH {BTC_VAH:,.0f} 是正常震荡区上沿。BTC 当前在 POC 上方、靠近价值区上半部，但仍未进入上沿执行带，不是自动做多或做空；今天下沿多头因 POC 过近而取消，只等待上沿冲高失败。")

    heading(doc, "S1-S5 Setup Scanner", 2)
    table(doc, ["Setup", "必要条件", "本轮结论"], [
        ["S1 流动性扫单", f"扫过VAL {BTC_VAL:,.0f}后快速收回，卖压减弱并形成HL", "本轮24h低点仍在 VAL 上方，尚未触达下沿扫单区"],
        ["S2c 趋势回踩", "4H趋势方向与回踩位置一致，反弹至EMA20/VAL后形成LH", "BTC/ETH处于过渡区，不给趋势回踩卡"],
        ["S3 去杠杆反转", "急跌、OI明显重置、Funding冷却、吸收并收回结构", "XRP有价格弱、OI增的分化，但未出现结构收回，不执行"],
        ["S4 题材轮动", "同一题材至少两个代表币、广度、独立催化与基本面共同确认", "AVAX/XRP/DOGE虽反弹，但没有同题材广度与基本面确认"],
        ["S5 区间均值回归", "触及VAL/VAH边缘并收回，最差入场R:R通过", f"下沿多头 INVALID；只保留上沿 {SHORT_ENTRY_LO:,.0f}-{SHORT_MAX:,.0f} 受阻做空"],
    ], font=7.0)
    paragraph(doc, f"现在 BTC 在 POC {BTC_POC:,.0f} 上方、处于价值区中上部，不能把反弹强度当成追多信号。今天下沿多头因 POC 过近而取消，空头只等上沿 {SHORT_ENTRY_LO:,.0f}-{SHORT_MAX:,.0f} 冲高失败。AVAX、XRP和DOGE没有形成同一题材的广度、主动买盘和基本面共振，S4仍不执行。")

    heading(doc, "第一优先级机会卡", 3)
    table(doc, ["资产", "方向 / Setup", "Regime", "为什么存在", "触发 / 当前价", "Ideal Entry", "Max Entry", "SL", "First Obstacle", "TP2", "净R:R", "状态", "Starter Risk", "加仓条件", "取消 / Missed"], [
        ["BTC", "S5上沿受阻空；下沿多 INVALID", "HTF_RANGE + RANGE_MIDDLE_UPPER_HALF", "现价位于POC上方、接近价值区上半部；下沿第一阻力过近，只有上沿有合格位置", f"空：触及 VAH {BTC_VAH:,.0f} 后跌回；现价 {btc_mark:,.0f}", f"空 {SHORT_IDEAL:,.0f}", f"空 {SHORT_MAX:,.0f}", f"空 {SHORT_STOP:,.0f}", f"空看 POC {BTC_POC:,.0f}", f"空看 VAL {BTC_VAL:,.0f}", f"空 1:{SHORT_WEIGHTED_RR:.2f}", "NOT TRIGGERED — WAIT", "最多0.10%账户风险上限", "跌回VAH下并形成LH", "重新站稳Max Entry即取消；超过Max Entry = MISSED — DO NOT CHASE"],
    ], font=5.8)
    paragraph(doc, f"这张卡不是现在立即下单：BTC 仍在中部。下沿多头因 POC 距离过近被取消；只有到上沿 {SHORT_ENTRY_LO:,.0f}-{SHORT_MAX:,.0f} 并出现受阻、跌回 VAH 下方形成 LH，才从等待进入执行判断；触发后也不能超过 Max Entry 追价。")

    heading(doc, "Opportunity Funnel", 2)
    table(doc, ["Universe", "映射位置", "风险通过候选", "预授权", "早期接受", "确认", "模型成交", "主要淘汰原因"], [
        ["13 个流动标的", "BTC价值区上沿 + S5", "1", "BTC上沿受阻空1张条件卡", "0", "0", "0", "下沿多头TP1净R:R不足；ETH/SOL未给更好位置；山寨未形成题材共振"],
    ], font=6.9)
    paragraph(doc, "扫描了13个流动标的，只有 BTC 上沿的 S5 受阻做空路径通过位置和动态盈亏比检查。下沿多头因第一阻力过近、TP1净R:R不足而 INVALID；当前空头卡仍未触发，没有模型成交，当前价附近不追单。")

    heading(doc, "Kelly 与组合风险", 2)
    table(doc, ["Setup", "Regime", "Historical N", "Wins", "p_raw", "p_adj", "Avg Win R", "Avg Loss R", "Expectancy R", "b", "Full Kelly", "Kelly Status"], [
        ["BTC S5 下沿收回多 / 上沿受阻空", "HTF_RANGE / RANGE_MIDDLE_UPPER_HALF", "0", "0", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "INSUFFICIENT_SAMPLE"],
    ], font=6.7)
    table(doc, ["Allowed Fraction", "Kelly Ceiling", "Setup Cap", "Regime Cap", "Correlation Cap", "Daily Remaining", "Final Allowed Risk", "Risk Mode"], [
        ["0", "0%", "0.75% hard ceiling", "0.25% ceiling", "BTC_CORE 0.80% ceiling", "UNKNOWN", "0.10% ceiling per card", "BOOTSTRAP_CALIBRATION"],
    ], font=6.9)
    table(doc, ["Evidence Source", "Setup Subtype", "Model N / User N", "Stop Distance", "Notional / Equity", "Leverage", "Margin / Equity", "Liquidation Buffer"], [
        ["Immutable model ledger", "S5_RANGE_EDGE_SWEEP_RECLAIM_REJECTION", "0 / UNKNOWN", f"{(SHORT_STOP-SHORT_MAX)/SHORT_MAX*100:.2f}%", f"{(0.001/((SHORT_STOP-SHORT_MAX)/SHORT_MAX))*100:.1f}%", "1x-2x", f"{(0.001/((SHORT_STOP-SHORT_MAX)/SHORT_MAX))*50:.1f}%-{(0.001/((SHORT_STOP-SHORT_MAX)/SHORT_MAX))*100:.1f}%", ">3x stop distance required"],
    ], font=6.8)
    paragraph(doc, "这里的0.10%是账户权益最大亏损预算，不是仓位占比，也不是要求一定用满。N=0只表示系统尚未积累同规则、同环境的已完成模型交易，并不表示用户亏了0笔或赚了0笔；Kelly不能启用，只能用极小Bootstrap测试上限。用户已有仓位未知，实际下单前还要从日内剩余风险中扣除。")

    heading(doc, "昨日框架复盘")
    table(doc, ["冻结计划", "有效期内真实路径", "模型结果", "预测质量", "本轮调整"], [
        ["BTC S5上沿受阻空；下沿多 INVALID", "上一版至本次刷新，没有可核验的模型成交证据；不回填后续价格", "UNTRIGGERED / INVALID_LONG / 未成交", "没有成交记录，不能把后续路径倒算成盈利或亏损", f"本次新快照把价值区重算为 VAL {BTC_VAL:,.0f} / POC {BTC_POC:,.0f} / VAH {BTC_VAH:,.0f}，下沿多头因第一阻力过近取消，仅保留上沿空头条件卡"],
    ], font=6.9)
    paragraph(doc, f"上一版条件卡没有可核验成交，因此不回填盈利或亏损。今天重新计算后，BTC 价值区为 VAL {BTC_VAL:,.0f}、POC {BTC_POC:,.0f}、VAH {BTC_VAH:,.0f}，当前 Regime 为4H区间、执行级别位于中上部；下沿多头因第一阻力过近取消，只保留上沿冲高失败做空。这是按新快照和新 Regime 重算，不是把旧计划改成盈利。")

    heading(doc, "核心市场状态仪表盘")
    table(doc, ["资产", "Mark / 24h", "VAL / POC / VAH", "Funding", "OI notional / 24h", "Taker 最近3h"], [
        [asset,
         f"{D['derivatives'][asset]['mark']:,.2f} / {D['derivatives'][asset]['change24']:+.2f}%",
         f"{P[asset]['val']:,.2f} / {P[asset]['poc']:,.2f} / {P[asset]['vah']:,.2f}",
         f"{D['derivatives'][asset]['funding']:+.4f}%",
         f"${D['derivatives'][asset]['oi_last']/1e9:.2f}bn / {D['derivatives'][asset]['oi24_pct']:+.2f}%",
         " / ".join(f"{x:.3f}" for x in D['derivatives'][asset]['taker_last3'])]
        for asset in ("BTC", "ETH", "SOL")
    ], font=7.0)
    paragraph(doc, f"VAL 是正常震荡区下沿，POC 是近期成交最集中的价格，VAH 是正常震荡区上沿。BTC、ETH、SOL 当前都在各自价值区内，其中 BTC 更靠近 POC，说明三者都不是价值区外的极端位置；这不等于自动追多或追空。BTC 最近一个 Taker 为 {D['derivatives']['BTC']['taker_last3'][-1]:.3f}，今天只有上沿冲高失败形成更低高点，才有空头交易依据；下沿多头要等价值区重算后第一阻力拉开。")
    add_picture(doc, CHARTS["levels"], "图1：BTC/ETH/SOL 最近 72 小时收盘与估算 5 日正常成交区。数据：Binance USDⓈ-M 1h；按每小时典型价格分配成交量，属于 PROXY。")

    heading(doc, "宏观与跨资产联动")
    macro_rows = [["美国 9月非农", "+29k vs 约 +84k 预期", "失业率 4.2%；工资 +0.1% m/m；前两月 -60k 修正", "增长降温，但 BTC 反应为先涨后跌，不能只按降息叙事交易"]]
    macro_rows.extend([
        name, f"{row['last']:,.2f}", f"{row['change_pct']:+.2f}%", "风险资产支持" if name in ("S&P 500", "Nasdaq") and row["change_pct"] >= 0 else "风险资产压制" if name in ("S&P 500", "Nasdaq") else "美元边际缓解" if name == "DXY" and row["change_pct"] < 0 else "美元边际压制" if name == "DXY" else "收益率回落，边际缓解" if name == "US10Y" and row["change_pct"] < 0 else "收益率上行形成压制" if name == "US10Y" else "跨资产背景"
    ] for name, row in D["macro"].items())
    table(doc, ["项目", "最新值/结果", "变化", "对加密的含义"], macro_rows, font=7.0)
    paragraph(doc, "今天的跨资产信号偏混合：标普和纳指上涨，提供风险偏好支持；但 DXY 与10年期收益率也上行，说明美元和利率仍有压制，黄金上涨又提示避险与通胀对冲需求。宏观没有给出可以覆盖技术结构的单边优势，因此不在 BTC POC 中部猜方向，只等待上沿受阻空；下沿多头因第一阻力过近暂不执行。")

    heading(doc, "大佬观点与叙事转向")
    table(doc, ["人物/机构", "核验结果", "此前 -> 当前", "本轮处理"], [
        ["Paul Atkins / SEC", "REPEATED_POLICY_ACTION", "从原则性支持走向10/1加密托管正式提案", "中期合规利多；今天无新增变化"],
        ["Cynthia Lummis / Senate", "NO_NEW_SCHEDULE", "支持 CLARITY；9/15 cloture 49-50 未通过", "没有新投票日，不列为当天催化"],
        ["Donald Trump / White House", "NO_VERIFIED_NEW_POLICY", "支持加密的总体立场未变", "争议性二手标题未获官方政策源确认，不提升权重"],
        ["Michael Saylor", "PRODUCT_PROMOTION", "继续长期看多BTC并推广STRC", "产品宣传不是新的宏观观点"],
        ["Ray Dalio", "NO_NEW_PRIMARY_UPDATE", "黄金为主、可配少量 BTC", "候选标题为旧观点再传播，本轮无新变化"],
        ["Larry Fink / Elizabeth Warren", "STALE / REPEATED", "代币化支持 / 监管批评", "均无足以改变仓位的新表态"],
    ], font=7.0)
    paragraph(doc, f"本轮监测了 {len(V['covered_universe'])} 位核心人物，抓到 {V['candidate_count']} 条候选标题，并对SEC、Senate、White House、Saylor、Dalio、BlackRock和Warren相关线索复核。结论是 NO_MATERIAL_CHANGE：不是没有抓取，而是没有新的、足以改变仓位或制度预期的立场变化。")

    heading(doc, "ETF、稳定币与市场流动性")
    flow_text = lambda value: "N/A" if value is None else f"{value:+.1f}m"
    table(doc, ["日期", "BTC ETF", "ETH ETF", "SOL ETF"], [[row["date"][5:], flow_text(row["BTC"]), flow_text(row["ETH"]), flow_text(row["SOL"])] for row in S["etf_flows_usd_m"]], font=7.3)
    btc5 = sum(row["BTC"] or 0 for row in S["etf_flows_usd_m"])
    eth5 = sum(row["ETH"] or 0 for row in S["etf_flows_usd_m"] if row["ETH"] is not None)
    sol5 = sum(row["SOL"] or 0 for row in S["etf_flows_usd_m"] if row["SOL"] is not None)
    paragraph(doc, f"已取得的最近发布日里，BTC ETF合计 {btc5:+.1f}m 美元；ETH {eth5:+.1f}m、SOL {sol5:+.1f}m 仅统计已公布的日子，10月7日 ETH/SOL 尚未完整取得，不能把 N/A 当成零流量。稳定币总供应约 ${D['stablecoins']['total_usd']/1e9:.1f}bn，提供中期流动性底座，但不能证明今天正在主动买币。")
    add_picture(doc, CHARTS["etf"], "图2：美国现货 ETF 最近 5 个发布日净流。BTC 最新公开值到 10 月 7 日；ETH/SOL 部分日期未公布。来源：公开 ETF 流数据汇总。")

    heading(doc, "巨鲸、财库与大额买卖盘")
    wt = D["whale_treasury_orderflow"]
    flow_rows, book_rows = [], []
    for asset in ("BTC", "ETH", "SOL"):
        item = wt["spot_orderflow"][asset]
        snap = item["venues"][item["preferred"]]
        tape = snap["trade_tape"]
        book = snap["order_book"]["0_5pct"]
        flow_rows.append([
            asset, snap["venue"], f"{tape['lookback_seconds']:.0f}s", f"${tape['large_threshold_usd']/1e3:.0f}k",
            f"${tape['large_buy_usd']/1e6:.2f}m / ${tape['large_sell_usd']/1e6:.2f}m", f"${tape['large_net_usd']/1e6:+.2f}m", f"{tape['buy_share']*100:.1f}%"
        ])
        book_rows.append([asset, f"${book['bid_usd']/1e6:.2f}m", f"${book['ask_usd']/1e6:.2f}m", f"{book['imbalance']*100:+.1f}%", "±0.5% visible book"])
    table(doc, ["资产", "现货场所", "样本窗", "大单门槛", "大单主动买/卖", "大单净额", "总买方占比"], flow_rows, font=6.8)
    table(doc, ["资产", "买方深度", "卖方深度", "盘口偏差", "口径"], book_rows, font=7.2)
    treasury = wt["treasury_monitor"]
    table(doc, ["财库主体", "最近披露买入", "总持仓", "总成本 / 均价", "文件日"], [[treasury["entity"], f"{treasury['acquired_btc']:,} BTC @ ${treasury['acquisition_average_usd']:,.0f}", f"{treasury['holdings_btc']:,} BTC", f"${treasury['aggregate_cost_usd_bn']:.2f}bn / ${treasury['average_cost_usd']:,.0f}", treasury["filing_date"]]], font=7.0)
    top_chain = [x for x in wt["onchain_large_transfers"].get("top_candidates", []) if x["btc"] >= 100][:3]
    chain_rows = [[f"{x['btc']:,.2f} BTC", f"${(x.get('usd') or 0)/1e6:.2f}m", x["txid"][:12] + "...", "PROXY / 地址未标注"] for x in top_chain]
    if not chain_rows:
        chain_rows = [["未发现 >=100 BTC", "不适用", "不适用", "最近10笔公开mempool短样本"]]
    table(doc, ["链上最近大额候选", "按现价折算", "Txid", "证据"], chain_rows, font=7.1)
    def tape_summary(asset_name: str) -> str:
        venue = wt.get("spot_orderflow", {}).get(asset_name, {}).get("venues", {}).get("binance")
        if not venue:
            return f"{asset_name} 现货主动买卖与盘口数据不可得"
        tape = venue["trade_tape"]
        book = venue["order_book"]["0_5pct"]
        return f"{asset_name} 主动净额 {tape['net_aggressive_usd']/1e6:+.2f}m、买方占比 {tape['buy_share']*100:.1f}%、盘口偏差 {book['imbalance']*100:+.1f}%"
    paragraph(doc, f"本轮 {tape_summary('BTC')}；{tape_summary('ETH')}；SOL 末端主动流量仍有修复，但不是持续买盘证据。标签化 CEX 钱包净流仍不可得，普通现货成交带不能冒充交易所净流。")

    heading(doc, "衍生品与微观结构")
    table(doc, ["资产", "价格24h", "Funding", "OI notional", "OI 24h", "Taker x3", "结构判断"], [
        [asset, f"{D['derivatives'][asset]['change24']:+.2f}%", f"{D['derivatives'][asset]['funding']:+.4f}%", f"${D['derivatives'][asset]['oi_last']/1e9:.2f}bn", f"{D['derivatives'][asset]['oi24_pct']:+.2f}%", "/".join(f"{x:.3f}" for x in D['derivatives'][asset]['taker_last3']),
         ("价格涨/OI增，反弹中有杠杆回补，末端仍未确认" if asset == "BTC" and D['derivatives'][asset]['change24'] >= 0 and D['derivatives'][asset]['oi24_pct'] >= 0 else
           "价格涨/OI增，反弹中有杠杆回补，末端Taker仍偏弱" if D['derivatives'][asset]['change24'] >= 0 and D['derivatives'][asset]['oi24_pct'] >= 0 else
          "价格跌/OI降，去杠杆进行中，末端Taker转弱" if D['derivatives'][asset]['change24'] < 0 and D['derivatives'][asset]['oi24_pct'] < 0 else
          "价格与OI方向分化，等待下一轮结构确认")]
        for asset in ("BTC", "ETH", "SOL")
    ], font=6.9)
    btc_dir = "上涨" if D["derivatives"]["BTC"]["change24"] >= 0 else "下跌"
    eth_dir = "上涨" if D["derivatives"]["ETH"]["change24"] >= 0 else "下跌"
    sol_dir = "上涨" if D["derivatives"]["SOL"]["change24"] >= 0 else "下跌"
    btc_oi_dir = "增加" if D["derivatives"]["BTC"]["oi24_pct"] >= 0 else "下降"
    eth_oi_dir = "增加" if D["derivatives"]["ETH"]["oi24_pct"] >= 0 else "下降"
    sol_oi_dir = "增加" if D["derivatives"]["SOL"]["oi24_pct"] >= 0 else "下降"
    paragraph(doc, f"BTC 24小时{btc_dir} {abs(D['derivatives']['BTC']['change24']):.2f}%、OI {btc_oi_dir} {abs(D['derivatives']['BTC']['oi24_pct']):.2f}%，最近三小时 Taker 为 {'、'.join(f'{x:.3f}' for x in D['derivatives']['BTC']['taker_last3'])}：价格与OI同步增加更像反弹中的杠杆回补，但末端 Taker 尚未稳定站上1.10，不能直接当成趋势反转。ETH 24小时{eth_dir} {abs(D['derivatives']['ETH']['change24']):.2f}%、OI {eth_oi_dir} {abs(D['derivatives']['ETH']['oi24_pct']):.2f}%；SOL 24小时{sol_dir} {abs(D['derivatives']['SOL']['change24']):.2f}%、OI {sol_oi_dir} {abs(D['derivatives']['SOL']['oi24_pct']):.2f}%。当前更像下跌后的修复与重新加杠杆混合，只有价格重新站回价值区、Taker持续改善且OI扩张不伴随冲高回落，才升级为趋势反转观察。")
    add_picture(doc, CHARTS["derivatives"], "图3：OI notional 六个日度观察、24h OI 变化、Funding 与最近三小时 Taker Buy/Sell Imbalance Proxy。Taker 比率不是 CVD。来源：Binance USDⓈ-M。")

    heading(doc, "期权、成本与持仓结构")
    table(doc, ["资产", "全期限 Put/Call OI", "近月到期", "近月 Put/Call", "派生 Max Pain", "高 OI 锚"], [
        ["BTC", f"{D['options']['BTC']['all_pc']:.2f}", D['options']['BTC']['near_expiry'], f"{D['options']['BTC']['near_pc']:.2f}", "N/A", "$90k / $95k / $100k calls"],
        ["ETH", f"{D['options']['ETH']['all_pc']:.2f}", D['options']['ETH']['near_expiry'], f"{D['options']['ETH']['near_pc']:.2f}", "N/A", "$2.5k puts / $3.2k-$3.5k calls"],
    ], font=7.0)
    table(doc, ["成本参考", "数值", "含义", "证据"], [
        ["Strategy 总持仓均价", "$75,437", "中期财库盈利区参考，不是市场平均成本", "SEC VERIFIED"],
        ["Strategy 最近披露买入均价", "$85,681", "当前价略低，可能形成公司最近批次的心理压力", "SEC VERIFIED"],
        ["链上 realized/STH cost", "UNAVAILABLE", "不能用财库成本替代全市场持有人成本", "公开同轮来源未取得"],
    ], font=7.0)
    paragraph(doc, f"BTC 全期限 Put/Call {D['options']['BTC']['all_pc']:.2f}、近月 {D['options']['BTC']['near_pc']:.2f}；ETH 全期限 {D['options']['ETH']['all_pc']:.2f}、近月 {D['options']['ETH']['near_pc']:.2f}。本轮只取得期权持仓结构，没有稳定的 Max Pain 数值，因此不把某个到期点当作价格目标；近月保护需求上升时，反弹更容易被对冲盘压住。")

    heading(doc, "Volume Profile、清算与筹码博弈")
    table(doc, ["资产", "VAL / 正常区下沿", "POC / 成交最密集", "VAH / 正常区上沿", "下方多头止损代理", "上方空头止损代理", "证据"], [
        ["BTC", f"{P['BTC']['val']:,.0f}", f"{P['BTC']['poc']:,.0f}", f"{P['BTC']['vah']:,.0f}", f"{P['BTC']['val']:,.0f} / {LONG_STOP:,.0f} / {SHORT_TP2:,.0f}", f"{P['BTC']['vah']:,.0f} / {SHORT_STOP:,.0f} / {P['BTC']['high']:,.0f}", "5d 1h profile PROXY + swing proxy"],
        ["ETH", f"{P['ETH']['val']:,.0f}", f"{P['ETH']['poc']:,.0f}", f"{P['ETH']['vah']:,.0f}", "2,617 / 2,580 / 2,500", "2,707 / 2,760 / 2,800", "5d 1h profile PROXY + swing proxy"],
        ["SOL", f"{P['SOL']['val']:,.2f}", f"{P['SOL']['poc']:,.2f}", f"{P['SOL']['vah']:,.2f}", "118.19 / 117.30 / 115.00", "121.71 / 123.00 / 124.00", "5d 1h profile PROXY + swing proxy"],
        ["AVAX", f"{ALT_PROFILES['AVAX']['val']:.4f}", f"{ALT_PROFILES['AVAX']['poc']:.4f}", f"{ALT_PROFILES['AVAX']['vah']:.4f}", f"{D['derivatives']['AVAX']['low24']:.4f} / {ALT_PROFILES['AVAX']['val']:.4f}", f"{ALT_PROFILES['AVAX']['vah']:.4f} / {D['derivatives']['AVAX']['high24']:.4f}", "5d 1h profile PROXY; derivative/liquidation available"],
        ["XRP", f"{ALT_PROFILES['XRP']['val']:.4f}", f"{ALT_PROFILES['XRP']['poc']:.4f}", f"{ALT_PROFILES['XRP']['vah']:.4f}", f"{D['derivatives']['XRP']['low24']:.4f} / {ALT_PROFILES['XRP']['val']:.4f}", f"{ALT_PROFILES['XRP']['vah']:.4f} / {D['derivatives']['XRP']['high24']:.4f}", "5d 1h profile PROXY; true liquidation heatmap unavailable"],
    ], font=6.4)
    paragraph(doc, f"POC 是近期成交最集中的价格，短线常像价格磁铁，但不是必然支撑；VAL 和 VAH 是覆盖约七成成交量的正常区下沿与上沿。BTC 当前在 VAL {BTC_VAL:,.0f} 与 VAH {BTC_VAH:,.0f} 之间、靠近 POC {BTC_POC:,.0f}，说明价格在正常成交区中部，不自动等于多头或空头；下沿扫低收回才有多头条件，上沿 {SHORT_ENTRY_LO:,.0f}-{SHORT_MAX:,.0f} 失败才有空头条件。AVAX 的 POC 约 {ALT_PROFILES['AVAX']['poc']:.4f}、XRP 的 POC 约 {ALT_PROFILES['XRP']['poc']:.4f}，只代表这五天成交最密集处。真实全网清算热力图本轮未取得，图中上下方数字只是止损/流动性代理，不代表真实清算金额。")
    add_picture(doc, CHARTS["profile"], "图4：左侧为 5 日 1h 典型价格分配的估算 Volume Profile；右侧为双向止损代理。蓝色为下方潜在多头止损，红色为上方潜在空头止损。不是 CoinGlass/Hyblock 真实清算热力图。")

    heading(doc, "盘面主线与板块轮动")
    ethbtc_now = D["derivatives"]["ETH"]["mark"] / D["derivatives"]["BTC"]["mark"]
    ethbtc_24 = float(D["derivatives"]["ETH"]["klines"][-25][4]) / float(D["derivatives"]["BTC"]["klines"][-25][4])
    table(doc, ["层级", "代表", "24h", "相对 BTC", "结论"], [
        ["Core", "BTC", f"{D['derivatives']['BTC']['change24']:+.2f}%", "基准", "ETF 5日净流为正，仍是资金主轴"],
        ["ETH beta", "ETH", f"{D['derivatives']['ETH']['change24']:+.2f}%", f"ETH/BTC {((ethbtc_now/ethbtc_24)-1)*100:+.2f}%", "跑输BTC，ETF仍流出"],
        ["Beta / payments", "SOL/AVAX/XRP", f"{D['derivatives']['SOL']['change24']:+.2f}% / {D['derivatives']['AVAX']['change24']:+.2f}% / {D['derivatives']['XRP']['change24']:+.2f}%", "XRP仅相对山寨抗跌，仍跑输BTC", "价格扩散失败，链上使用未同步"],
        ["Other liquid alts", "LINK/XRP/DOGE", f"{D['derivatives']['LINK']['change24']:+.2f}% / {D['derivatives']['XRP']['change24']:+.2f}% / {D['derivatives']['DOGE']['change24']:+.2f}%", "普遍弱于BTC", "不是全面山寨季"],
    ], font=7.0)
    paragraph(doc, "今早山寨出现普遍反弹，但还不是已经确认的轮动扩散：AVAX、XRP、DOGE均上涨，OI变化分化，尚未证明有持续的主题资金进场。价格反弹不能单独升级为 S4，必须等同题材广度、主动买盘和可核验链上使用一起改善。")

    heading(doc, "山寨币题材分层与基本面")
    table(doc, ["题材/标的", "相对强弱", "网络使用/收入", "Tokenomics", "资金/叙事归因", "交易结论"], [
        ["L1 / AVAX", f"相对BTC {S['alt_snapshot']['AVAX']['change24_pct']-D['derivatives']['BTC']['change24']:+.2f}pp", f"TVL ${S['alt_fundamentals']['AVAX']['tvl_usd']/1e6:.1f}m；7d {S['alt_fundamentals']['AVAX']['tvl_7d_pct']:+.2f}%；DEX量7d {S['alt_fundamentals']['AVAX']['dex_volume_7d_pct']:+.2f}%；费用未取得", "公开解锁字段本轮未核验", f"价格 {S['alt_snapshot']['AVAX']['change24_pct']:+.2f}%；OI {S['alt_snapshot']['AVAX']['oi24_pct']:+.2f}%；Funding {S['alt_snapshot']['AVAX']['funding_pct']:+.4f}%；Taker {S['alt_snapshot']['AVAX']['taker_last']:.3f}", "研究Top2；相对BTC偏弱，不单独交易"],
        ["支付 / XRP", f"相对BTC {S['alt_snapshot']['XRP']['change24_pct']-D['derivatives']['BTC']['change24']:+.2f}pp", "TVL/DEX收入本轮不可得；不把价格上涨当作使用增长", "公开解锁字段本轮未核验", f"价格 {S['alt_snapshot']['XRP']['change24_pct']:+.2f}%；OI {S['alt_snapshot']['XRP']['oi24_pct']:+.2f}%；Funding {S['alt_snapshot']['XRP']['funding_pct']:+.4f}%；Taker {S['alt_snapshot']['XRP']['taker_last']:.3f}", "研究Top1；叙事/资金驱动，不给交易卡"],
    ], font=6.5)
    paragraph(doc, "本轮 Alpha 研究仍只保留 AVAX 与 XRP：两者价格相对 BTC 有所修复，但尚未形成独立强势；AVAX 的链上数据只有部分可得，XRP 的使用与解锁数据不可得。它们没有同时通过相对强弱、资金流、基本面和供给闸门，因此没有给山寨交易卡；DOGE只作为高波动模因风险提示。")
    add_picture(doc, CHARTS["alt"], "图5：Top-2山寨研究标的相对BTC的24h表现与经核验的7日DEX成交量变化。价格强不等于链上使用同步改善。")

    heading(doc, "S4 Rotation Research")
    table(doc, ["检查项", "AVAX", "XRP", "S4 结论"], [
        ["相对BTC", f"{S['alt_snapshot']['AVAX']['change24_pct']-D['derivatives']['BTC']['change24']:+.2f}pp", f"{S['alt_snapshot']['XRP']['change24_pct']-D['derivatives']['BTC']['change24']:+.2f}pp", "有修复但未形成持续扩散"],
        ["同题材广度", "L1", "支付/监管beta", "不是同题材扩散"],
        ["Flow/OI", f"OI {S['alt_snapshot']['AVAX']['oi24_pct']:+.2f}%，Taker {S['alt_snapshot']['AVAX']['taker_last']:.3f}", f"OI {S['alt_snapshot']['XRP']['oi24_pct']:+.2f}%，Taker {S['alt_snapshot']['XRP']['taker_last']:.3f}", "资金有修复，但不足以确认主线"],
        ["基本面/解锁", "TVL 7d +1.85%，DEX量7d -4.76%，解锁未核验", "TVL/DEX/解锁本轮不可得", "基本面/供给闸门未通过"],
        ["最终", "Research Top2", "Research Top1", "NO EXECUTABLE ROTATION"],
    ], font=7.0)
    paragraph(doc, "S4 的价格广度本轮仍没有通过：AVAX 和 XRP 虽然反弹，但没有同一题材的第二、第三个代表币同步确认，且链上基本面与解锁闸门不完整。因此只保留 AVAX/XRP 研究，不给山寨交易卡。")

    heading(doc, "预测回测与 Setup Performance")
    table(doc, ["维度", "截至本轮", "本轮新增", "解释"], [
        ["Forecast Accuracy", "昨日下沿限价区未触达", "UNTRIGGERED", "价格路径判断与交易成交分开统计"],
        ["Completed Model Trades", "0", "0", "昨日卡未触发，不能回填成交"],
        ["S5 RANGE_EDGE N", "0", "0", "Kelly 仍无资格"],
        ["User Realized Ledger", "UNKNOWN", "UNKNOWN", "没有用户成交确认"],
        ["Counterfactual", "不适用", "N/A", "价格始终未触及旧入场区"],
    ], font=7.1)
    paragraph(doc, "上一版 BTC S5 条件卡没有可核验成交，所以没有模型交易，也不能计入 Kelly。今天下沿多头因第一阻力过近取消，只保留‘反弹失败做空’路径；有效卡的最大风险预算仍是0.10%，不是要求必须用满的目标仓位。")

    heading(doc, "未来大事催化")
    catalyst_rows = []
    for event in S["catalysts"]:
        impact = "DXY/收益率 -> BTC/ETH/SOL" if "US " in event["event"] or "FOMC" in event["event"] else "SOL 供应节奏" if "Solana" in event["event"] else "LINK 基础设施预期" if "Chainlink" in event["event"] else "美国加密监管"
        state = "已落地" if event["classification"] == "Event Outcome" else "待公布"
        confirmation = "公布后15m价格、收益率、DXY与OI同向" if state == "待公布" and impact.startswith("DXY") else "规模保持低于1%流通量" if "Solana" in event["event"] else "测试按期完成且无故障" if "Chainlink" in event["event"] else "新投票日期/正式议程"
        invalidation = "日期更改或官方取消" if state == "待公布" else "没有新议程前不当未来催化"
        catalyst_rows.append([event["time_bjt"], event["classification"], event["event"], state, event["first_confirmed"], event["incremental_change"], event["assets"], impact, confirmation, invalidation])
    table(doc, ["时间 BJT", "分类", "事件", "状态", "首次确认", "本次新增", "资产", "传导", "确认", "失效/处理"], catalyst_rows, font=5.5)
    paragraph(doc, "已发生或计划日期已过去的事件不会因为当天没有新消息就从时间线消失；报告把它们标为‘已落地’，并单独写首次确认时间和本次是否新增。10月13日 Solana staking rewards、10月8日稳定币与10月9日 MOVE 解锁的计划时间都已过去，但本轮没有取得实际结果，因此保留为已落地事件而不是重新列为待公布。下一项正式宏观节点是10月14日CPI；CLARITY投票结果没有新日期，只保留历史结果。")

    heading(doc, "明日观察清单")
    table(doc, ["优先级", "观察点", "具体判定", "对应动作"], [
        ["1", "BTC 上沿受阻空", f"{SHORT_ENTRY_LO:,.0f}-{SHORT_MAX:,.0f}是否触达；15m/30m能否冲高失败、跌回VAH {BTC_VAH:,.0f}下方并形成LH", "最多0.10%风险；站回Max Entry即取消"],
        ["2", "BTC 反弹失败空", f"{SHORT_ENTRY_LO:,.0f}-{SHORT_MAX:,.0f}是否触达；反弹后能否重新跌回VAL下方并形成LH", "最多0.10%风险；站回Max Entry即取消"],
        ["3", "杠杆", f"BTC OI增加后是否继续；Taker能否从{D['derivatives']['BTC']['taker_last3'][-1]:.3f}回落并再次转弱", "区分反抽修复与二次下压"],
        ["4", "ETF", "BTC 流入能否扩张、ETH 是否结束连续流出", "判断资金是否从 BTC 向 beta 扩散"],
        ["5", "山寨广度", "AVAX/XRP能否形成同题材扩散，并且Taker与可核验链上指标共同改善", "否则只保留研究主线"],
    ], font=7.0)
    paragraph(doc, f"下一轮最重要的不是猜 BTC 会涨还是跌，而是观察上沿 {SHORT_ENTRY_LO:,.0f}-{SHORT_MAX:,.0f} 是否出现冲高失败。今天 VAL {BTC_VAL:,.0f} 附近即使收回，也因 POC {BTC_POC:,.0f} 过近而不能直接做多；只有价值区重算后第一阻力重新拉开，才恢复多头评估。当前价附近不追空，也不直接抄底。")

    heading(doc, "数据与来源")
    table(doc, ["模块", "主源/备用", "观察时间", "结果", "证据"], [
        ["价格/衍生品", "Binance USDⓈ-M direct API", D["retrieved_bjt"], "SUCCESS", "VERIFIED"],
        ["现货大单/盘口", "Binance Spot / OKX fallback", wt["retrieved_bjt"], wt["status"], "VERIFIED per successful venue"],
        ["宏观/事件", "Federal Reserve, BLS, BEA; Yahoo cross-asset", f"{D['retrieved_bjt'][:10]} {D['retrieved_bjt'][11:16]} BJT", "SUCCESS", "VERIFIED / latest market close"],
        ["BTC/ETH/SOL ETF", "CryptoMeter / Alpha Finance; Farside fallback", "published through 2026-10-07 for BTC; ETH/SOL partial", "PARTIAL", "SECONDARY"],
        ["稳定币", "DefiLlama stablecoin API", D["retrieved_bjt"], "SUCCESS", "SECONDARY"],
        ["财库", "SEC EDGAR Strategy 8-K", treasury["filing_date"], "SUCCESS", "VERIFIED"],
        ["链上大额候选", "mempool.space recent tx", wt["retrieved_bjt"], "SUCCESS", "PROXY / unlabeled"],
        ["标签化 CEX 钱包净流", "Public exchange API check / no authenticated labelled provider", D["retrieved_bjt"], "UNAVAILABLE", "UNAVAILABLE"],
        ["期权", "Deribit public API; local max-pain derivation", D["retrieved_bjt"], "SUCCESS", "VERIFIED + DERIVED"],
        ["链上 realized/STH cost", "Public-source scan", "2026-10-13", "UNAVAILABLE", "UNAVAILABLE"],
        ["Volume Profile", "Binance 1h OHLCV typical-price allocation", D["retrieved_bjt"], "SUCCESS", "PROXY"],
        ["真实清算热力图", "CoinGlass/Hyblock lawful public access", "2026-10-13", "UNAVAILABLE", "UNAVAILABLE; stop proxy shown separately"],
        ["山寨基本面/解锁", "DefiLlama chain/unlock pages", "2026-10-13", "PARTIAL; AVAX only", "SECONDARY"],
        ["大佬观点", "Google News candidate monitor + SEC/Senate/White House/issuer checks", V["cutoff_bjt"], V["status"], "VERIFIED where promoted"],
        ["未来催化", "Federal Reserve/BLS/BEA/Senate/DefiLlama calendars", "2026-10-13", "SUCCESS", "VERIFIED / SECONDARY unlock"],
    ], font=6.4)
    paragraph(doc, "来源：Binance/OKX、Deribit、BLS、Fed、BEA、Farside、SEC EDGAR、mempool.space、DefiLlama；代理数据均已在正文单列。", size=8.8, after=0)

    doc.core_properties.title = "加密宏观每日复盘 - 2026-10-13"
    doc.core_properties.subject = "BTC/ETH/SOL 宏观、衍生品、交易台与风险复盘"
    doc.core_properties.author = "Codex"
    doc.save(OUT)
    return OUT


def write_state_and_ledger(report_path: Path) -> None:
    root = OUT_ROOT / "execution_learning"
    root.mkdir(parents=True, exist_ok=True)
    state = {
        "timestamp_bjt": D["retrieved_bjt"],
        "rule_version": "crypto-macro-daily-review-s1-s5-dynamic-rr-v1 + crypto-macro-daily-review-execution-learning-v2",
        "report_file": report_path.name,
        "regime": "HTF_RANGE_RANGE_MIDDLE_UPPER_HALF",
        "bias": "MEDIUM_TERM_RANGE_CURRENT_UPPER_HALF",
        "major_levels": {asset: {key: P[asset][key] for key in ("val", "poc", "vah", "low", "high")} for asset in ("BTC", "ETH", "SOL")},
        "active_candidate": "20261013-0811-btc-s5-upper-rejection",
        "now_action": "WAIT_NOW",
        "next_valid_plan": "ARMED_SHORT_ONLY",
        "data_quality": "B",
        "key_data_gap": "labelled CEX wallet netflow and true provider liquidation heatmap unavailable"
    }
    (root / "daily_market_state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    ledger = root / "model_execution_ledger.jsonl"
    setup_id = "20261013-0811-btc-s5-upper-rejection"
    existing = ledger.read_text(encoding="utf-8") if ledger.exists() else ""
    if f'"setup_id": "{setup_id}"' not in existing:
        event = {
            "timestamp_bjt": D["retrieved_bjt"], "event_type": "CANDIDATE", "setup_id": setup_id,
            "asset": "BTC", "direction": "SHORT", "setup_type": "S5", "setup_subtype": "RANGE_EDGE_REJECTION",
            "rule_version": "crypto-macro-daily-review-s1-s5-dynamic-rr-v1", "regime": "HTF_RANGE_RANGE_MIDDLE_UPPER_HALF",
            "model_status": "ARMED", "entry_method": "CONDITIONAL_LIMIT_PROBE", "ideal_entry": SHORT_IDEAL,
            "max_entry": SHORT_MAX, "stop": SHORT_STOP, "first_obstacle": SHORT_TP1, "tp2": SHORT_TP2,
            "gross_rr_obstacle": round((SHORT_MAX - SHORT_TP1) / (SHORT_STOP - SHORT_MAX), 3),
            "gross_rr_tp2": round((SHORT_MAX - SHORT_TP2) / (SHORT_STOP - SHORT_MAX), 3),
            "net_rr_obstacle": round(SHORT_RR1, 3), "net_rr_tp2": round(SHORT_RR2, 3), "weighted_net_rr": round(SHORT_WEIGHTED_RR, 3),
            "estimated_fee_rate": 0.0008, "estimated_slippage_rate": 0.0004,
            "model_allowed_risk_pct": 0.10, "risk_mode": "BOOTSTRAP_CALIBRATION", "correlation_cluster": "BTC_CORE",
            "entry_expiry": "2026-10-13T20:00:00+08:00", "data_quality": "B", "event_risk": "MEDIUM",
            "trigger": f"Short only: rebound into {SHORT_ENTRY_LO:.0f}-{SHORT_MAX:.0f}, fail back below VAH with lower high and weak Taker. Lower-edge long is invalid because TP1 net R:R is below threshold.",
            "flow_confirmation_status": "REQUIRED_FOR_TRIGGER", "flow_mode": "S5_RANGE_EDGE_SWEEP_RECLAIM_OR_REJECTION",
            "structural_zone_id": "BTC-5D-VALUE-20261013-0811", "structural_zone_status": "VALID", "attempt_id": "attempt01",
            "attempt_status": "NOT_STARTED", "fresh_trigger_id": None, "attempt_count": 0, "rearm_eligible": True,
            "counterfactual_status": "NOT_APPLICABLE"
        }
        with ledger.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    output = make_document()
    write_state_and_ledger(output)
    print(output)





