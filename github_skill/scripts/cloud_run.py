from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


BJT = ZoneInfo("Asia/Shanghai")
NOW = datetime.now(BJT)
BUNDLE = Path(__file__).resolve().parents[1]
REPORTS = BUNDLE / "reports"
CONFIG = BUNDLE / "config" / "active_conditions.json"
REPORTS.mkdir(parents=True, exist_ok=True)
CONFIG.parent.mkdir(parents=True, exist_ok=True)


def run_fetch() -> Path:
    subprocess.run([sys.executable, str(BUNDLE / "scripts" / "cloud_fetch.py")], cwd=BUNDLE, check=True)
    data_path = BUNDLE / f"live_market_detail_{NOW:%Y%m%d}.json"
    if not data_path.exists():
        raise FileNotFoundError(data_path)
    return data_path


def make_research_inputs(data_path: Path) -> tuple[Path, Path]:
    data = json.loads(data_path.read_text(encoding="utf-8"))
    stamp = data.get("retrieved_bjt", NOW.isoformat())
    tag = NOW.strftime("%H%M")
    supplement = json.loads((BUNDLE / "templates" / "research_supplement_template.json").read_text(encoding="utf-8"))
    supplement["snapshot_bjt"] = stamp
    supplement["options_derived"] = {
        "BTC_near_expiry": data.get("options", {}).get("BTC", {}).get("near_expiry"),
        "ETH_near_expiry": data.get("options", {}).get("ETH", {}).get("near_expiry"),
        "BTC_near_max_pain": "UNAVAILABLE_THIS_RUN",
        "ETH_near_max_pain": "UNAVAILABLE_THIS_RUN",
        "method": "Deribit public open-interest snapshot; max-pain not recalculated into a stable numeric level in this run",
        "evidence": "DERIBIT_VERIFIED / DERIVED_PARTIAL",
    }
    for asset in ("AVAX", "XRP", "DOGE"):
        item = data.get("derivatives", {}).get(asset)
        if item:
            supplement.setdefault("alt_snapshot", {})[asset] = {
                "change24_pct": item.get("change24"),
                "oi24_pct": item.get("oi24_pct"),
                "funding_pct": item.get("funding"),
                "taker_last": item.get("taker_last3", [None])[-1],
            }
    supplement_path = BUNDLE / f"research_supplement_{NOW:%Y%m%d}_{tag}.json"
    supplement_path.write_text(json.dumps(supplement, ensure_ascii=False, indent=2), encoding="utf-8")

    views = json.loads((BUNDLE / "templates" / "verified_updates_template.json").read_text(encoding="utf-8"))
    views["cutoff_bjt"] = stamp
    views_path = BUNDLE / f"verified_updates_{NOW:%Y%m%d}_{tag}.json"
    views_path.write_text(json.dumps(views, ensure_ascii=False, indent=2), encoding="utf-8")
    return supplement_path, views_path


def build_report(data_path: Path, supplement_path: Path, views_path: Path) -> Path:
    template = (BUNDLE / "templates" / "build_daily_template.py").read_text(encoding="utf-8")
    today_iso = NOW.strftime("%Y-%m-%d")
    today_compact = NOW.strftime("%Y%m%d")
    tag = NOW.strftime("%H%M")
    replacements = {
        'PROJECT = Path(r"D:\\codex\\技能项目\\crypto_macro_daily")': 'PROJECT = Path(os.environ["CRYPTO_GITHUB_ROOT"])',
        'OUT_ROOT = Path(r"D:\\codex\\crypto_macro_daily")': 'OUT_ROOT = Path(os.environ["CRYPTO_REPORT_ROOT"])',
        'sys.path.insert(0, r"D:\\codex\\skills\\crypto-macro-daily-review\\scripts")': 'sys.path.insert(0, str(PROJECT / "scripts"))',
        "live_market_detail_20261013.json": data_path.name,
        "research_supplement_20261013_0811.json": supplement_path.name,
        "verified_updates_20261013_0811.json": views_path.name,
        "2026-10-13": today_iso,
        "20261013": today_compact,
        "0811": tag,
    }
    for old, new in replacements.items():
        template = template.replace(old, new)
    generated = BUNDLE / f"_build_daily_{today_compact}_{tag}.py"
    generated.write_text(template, encoding="utf-8")
    env = os.environ.copy()
    env["CRYPTO_GITHUB_ROOT"] = str(BUNDLE)
    env["CRYPTO_REPORT_ROOT"] = str(REPORTS)
    subprocess.run([sys.executable, str(generated)], cwd=BUNDLE, env=env, check=True)
    reports = sorted(REPORTS.glob("crypto_macro_daily_*.docx"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not reports:
        raise FileNotFoundError("No Word report generated")
    return reports[0]


def profile(candles: list[list[object]]) -> dict[str, float]:
    rows = candles[:-1]
    typical = [(float(x[2]) + float(x[3]) + float(x[4])) / 3 for x in rows]
    low, high = min(typical), max(typical)
    width = (high - low) / 50 or 1.0
    bins: defaultdict[int, float] = defaultdict(float)
    for candle, price in zip(rows, typical):
        bins[min(49, int((price - low) / width))] += float(candle[5]) * price
    poc_i = max(bins, key=bins.get)
    selected, included = {poc_i}, bins[poc_i]
    total = sum(bins.values())
    left, right = poc_i - 1, poc_i + 1
    while included < total * 0.70:
        if right < 50 and (left < 0 or bins.get(right, 0) >= bins.get(left, 0)):
            selected.add(right); included += bins.get(right, 0); right += 1
        else:
            selected.add(left); included += bins.get(left, 0); left -= 1
    return {"val": low + min(selected) * width, "poc": low + (poc_i + 0.5) * width, "vah": low + (max(selected) + 1) * width}


def rr(entry: float, stop: float, target: float, side: str) -> float:
    cost = entry * 0.0012
    risk = abs(entry - stop) + cost
    reward = (target - entry) if side == "long" else (entry - target)
    return (reward - cost) / risk


def update_conditions(data_path: Path) -> None:
    data = json.loads(data_path.read_text(encoding="utf-8"))
    assets: dict[str, dict[str, object]] = {}
    for symbol, asset in (("BTCUSDT", "BTC"), ("ETHUSDT", "ETH"), ("SOLUSDT", "SOL")):
        p = profile(data["derivatives"][asset]["klines"])
        long_max, long_stop = p["val"] + 50, p["val"] - 500
        short_max, short_stop = p["vah"] + 80, p["vah"] + 500
        long_ok = rr(long_max, long_stop, p["poc"], "long") >= 1.0 and (0.4 * rr(long_max, long_stop, p["poc"], "long") + 0.6 * rr(long_max, long_stop, p["vah"], "long")) >= 1.3
        short_ok = rr(short_max, short_stop, p["poc"], "short") >= 1.0 and (0.4 * rr(short_max, short_stop, p["poc"], "short") + 0.6 * rr(short_max, short_stop, p["val"], "short")) >= 1.3
        assets[symbol] = {
            "long_zone": [round(p["val"] - 100, 2), round(long_max, 2)] if long_ok else [],
            "short_zone": [round(p["vah"] - 100, 2), round(short_max, 2)] if short_ok else [],
            "alerted_long": False,
            "alerted_short": False,
        }
    CONFIG.write_text(json.dumps({"date": NOW.strftime("%Y-%m-%d"), "assets": assets}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    data_path = run_fetch()
    supplement_path, views_path = make_research_inputs(data_path)
    report = build_report(data_path, supplement_path, views_path)
    update_conditions(data_path)
    print(json.dumps({"report": str(report), "conditions": str(CONFIG)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
