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
BUSINESS_DATE = NOW.date().isoformat()
BUNDLE = Path(__file__).resolve().parents[1]
REPO_ROOT = BUNDLE.parent
REPORTS = REPO_ROOT / "reports"
CONFIG = REPO_ROOT / "config" / "active_conditions.json"
AUDIT = REPO_ROOT / "audit"
REPORTS.mkdir(parents=True, exist_ok=True)
CONFIG.parent.mkdir(parents=True, exist_ok=True)
AUDIT.mkdir(parents=True, exist_ok=True)


def run_fetch() -> Path:
    subprocess.run([sys.executable, str(BUNDLE / "scripts" / "cloud_fetch.py")], cwd=BUNDLE, check=True)
    data_path = BUNDLE / f"live_market_detail_{NOW:%Y%m%d}.json"
    if not data_path.exists():
        raise FileNotFoundError(data_path)
    return data_path


def make_research_inputs(data_path: Path) -> tuple[Path, Path]:
    data = json.loads(data_path.read_text(encoding="utf-8"))
    stamp = data.get("retrieved_bjt", NOW.isoformat())
    tag = NOW.strftime("%H%M%S")
    supplement = json.loads((BUNDLE / "templates" / "research_supplement_template.json").read_text(encoding="utf-8"))
    supplement["snapshot_bjt"] = stamp
    # Reconcile known scheduled releases against the current snapshot. These
    # outcomes were verified from the official BLS releases; they must not
    # remain a stale "待公布" event after their release window has passed.
    verified_outcomes = {
        "US September CPI": {
            "classification": "Event Outcome",
            "incremental_change": "已落地：CPI-U 9月环比 +0.6%，同比 +3.7%；能源价格上升是主要推动项。",
            "source": "https://www.bls.gov/news.release/archives/cpi_10142026.htm",
        },
        "US September PPI": {
            "classification": "Event Outcome",
            "incremental_change": "已落地：最终需求PPI 9月环比 +1.3%，为2022年3月以来最大月度涨幅。",
            "source": "https://www.bls.gov/news.release/archives/ppi_10152026.htm",
        },
    }
    for event in supplement.get("catalysts", []):
        outcome = verified_outcomes.get(event.get("event"))
        if outcome:
            event.update(outcome)
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
    # The candidate monitor is run as part of the live fetch.  Do not let the
    # report fall back to a stale hand-written key-person status when today's
    # monitor has a fresh result.
    monitor = data.get("key_person_monitor", {})
    if monitor:
        scan_status = monitor.get("scan_status")
        validated = monitor.get("validated_updates") or []
        views["status"] = "NEW_OR_CHANGED_VIEW" if validated else (
            "NO_MATERIAL_CHANGE" if scan_status == "SUCCESS" else "DATA_COLLECTION_FAILED"
        )
        views["covered_universe"] = monitor.get("covered_people") or views.get("covered_universe", [])
        views["candidate_count"] = monitor.get("candidate_count", 0)
        views["updates"] = validated
        views["primary_or_credible_checks"] = [{
            "person": "Automated key-person candidate monitor",
            "result": scan_status or "UNKNOWN",
            "note": monitor.get("note", "")
        }]
    views_path = BUNDLE / f"verified_updates_{NOW:%Y%m%d}_{tag}.json"
    views_path.write_text(json.dumps(views, ensure_ascii=False, indent=2), encoding="utf-8")
    return supplement_path, views_path


def build_report(data_path: Path, supplement_path: Path, views_path: Path) -> Path:
    template = (BUNDLE / "templates" / "build_daily_template.py").read_text(encoding="utf-8")
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    tag = NOW.strftime("%Y-%m-%d_%H%M%SBJT")
    candidate = REPORTS / f"crypto_macro_daily_{tag}.docx"
    if candidate.exists():
        tag = f"{NOW:%Y-%m-%d_%H%M%SBJT}_r{run_id}"
    generated = BUNDLE / f"_build_daily_{NOW:%Y%m%d}_{NOW:%H%M%S}_{run_id}.py"
    generated.write_text(template, encoding="utf-8")
    env = os.environ.copy()
    env["CRYPTO_GITHUB_ROOT"] = str(BUNDLE)
    env["CRYPTO_REPORT_ROOT"] = str(REPORTS)
    env["CRYPTO_DATA_FILE"] = data_path.name
    env["CRYPTO_SUPPLEMENT_FILE"] = supplement_path.name
    env["CRYPTO_VIEWS_FILE"] = views_path.name
    env["CRYPTO_REPORT_TAG"] = tag
    subprocess.run([sys.executable, str(generated)], cwd=BUNDLE, env=env, check=True)
    report = REPORTS / f"crypto_macro_daily_{tag}.docx"
    if not report.exists():
        raise FileNotFoundError(report)
    return report


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
    previous: dict[str, object] = {}
    if CONFIG.exists():
        try:
            previous = json.loads(CONFIG.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            previous = {}
    same_business_date = previous.get("date") == BUSINESS_DATE
    previous_assets = previous.get("assets", {}) if isinstance(previous.get("assets", {}), dict) else {}
    assets: dict[str, dict[str, object]] = {}
    for symbol, asset in (("BTCUSDT", "BTC"), ("ETHUSDT", "ETH"), ("SOLUSDT", "SOL")):
        p = profile(data["derivatives"][asset]["klines"])
        long_max, long_stop = p["val"] + 50, p["val"] - 500
        short_max, short_stop = p["vah"] + 80, p["vah"] + 500
        long_ok = rr(long_max, long_stop, p["poc"], "long") >= 1.0 and (0.4 * rr(long_max, long_stop, p["poc"], "long") + 0.6 * rr(long_max, long_stop, p["vah"], "long")) >= 1.3
        short_ok = rr(short_max, short_stop, p["poc"], "short") >= 1.0 and (0.4 * rr(short_max, short_stop, p["poc"], "short") + 0.6 * rr(short_max, short_stop, p["val"], "short")) >= 1.3
        old = previous_assets.get(symbol, {}) if isinstance(previous_assets.get(symbol, {}), dict) else {}
        long_zone = [round(p["val"] - 100, 2), round(long_max, 2)] if long_ok else []
        short_zone = [round(p["vah"] - 100, 2), round(short_max, 2)] if short_ok else []
        assets[symbol] = {
            "long_zone": long_zone,
            "short_zone": short_zone,
            "alerted_long": bool(same_business_date and old.get("long_zone") == long_zone and old.get("alerted_long", False)),
            "alerted_short": bool(same_business_date and old.get("short_zone") == short_zone and old.get("alerted_short", False)),
        }
    sent_alerts = previous.get("sent_alerts", {}) if same_business_date and isinstance(previous.get("sent_alerts", {}), dict) else {}
    CONFIG.write_text(json.dumps({"date": BUSINESS_DATE, "assets": assets, "sent_alerts": sent_alerts}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_audit(record: dict[str, object]) -> None:
    run_id = str(record.get("run_id", "local"))
    (AUDIT / f"daily_review_{run_id}.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def existing_success_for_business_date() -> dict[str, object] | None:
    canonical = AUDIT / f"daily_review_{BUSINESS_DATE}.json"
    if not canonical.exists():
        return None
    try:
        record = json.loads(canonical.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return record if record.get("generation_status") == "SUCCESS" else None


def main() -> None:
    prior = existing_success_for_business_date()
    if prior and os.environ.get("ALLOW_DAILY_REBUILD") != "1":
        record = {
            "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
            "report_date": BUSINESS_DATE,
            "generated_at_bjt": NOW.isoformat(),
            "generation_status": "DUPLICATE_SKIP",
            "reused_report": prior.get("report"),
            "reused_html": prior.get("html"),
            "note": "A successful report already exists for this business date; no historical report was overwritten.",
            "data_sources": prior.get("data_sources"),
        }
        write_audit(record)
        print(json.dumps(record, ensure_ascii=False))
        return
    data_path = run_fetch()
    supplement_path, views_path = make_research_inputs(data_path)
    report = build_report(data_path, supplement_path, views_path)
    html_path = REPORTS / f"{report.stem}.html"
    subprocess.run(
        [sys.executable, str(BUNDLE / "scripts" / "docx_to_html.py"), str(report), str(html_path)],
        cwd=BUNDLE,
        check=True,
    )
    shutil.copyfile(html_path, REPORTS / "index.html")
    update_conditions(data_path)
    data = json.loads(data_path.read_text(encoding="utf-8"))
    audit = {
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "workflow_event": os.environ.get("GITHUB_EVENT_NAME"),
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "planned_run_bjt": f"{BUSINESS_DATE}T07:05:00+08:00",
        "actual_run_bjt": NOW.isoformat(),
        "retrieved_bjt": data.get("retrieved_bjt"),
        "report_date": BUSINESS_DATE,
        "generated_at_bjt": NOW.isoformat(),
        "report": str(report.relative_to(REPO_ROOT)),
        "html": str(html_path.relative_to(REPO_ROOT)),
        "index_html": "reports/index.html",
        "active_conditions": str(CONFIG.relative_to(REPO_ROOT)),
        "generation_status": "SUCCESS",
        "data_sources": data.get("data_source_audit"),
    }
    write_audit(audit)
    (AUDIT / f"daily_review_{BUSINESS_DATE}.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(report), "html": str(html_path), "conditions": str(CONFIG), "audit": str(AUDIT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
