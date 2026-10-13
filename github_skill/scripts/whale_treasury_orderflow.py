from __future__ import annotations

import argparse
import html
import json
import math
import re
from datetime import datetime
from pathlib import Path
from statistics import quantiles
from typing import Any
from zoneinfo import ZoneInfo

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


BJT = ZoneInfo("Asia/Shanghai")
ASSETS = {
    "BTC": {"binance": "BTCUSDT", "okx": "BTC-USDT", "floor": 250_000},
    "ETH": {"binance": "ETHUSDT", "okx": "ETH-USDT", "floor": 150_000},
    "SOL": {"binance": "SOLUSDT", "okx": "SOL-USDT", "floor": 100_000},
}
STRATEGY_CIK = "0001050446"


def session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=2,
        connect=2,
        read=2,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers.update(
        {
            "User-Agent": "CodexResearch crypto-data admin@example.com",
            "Accept": "application/json,text/plain,*/*",
        }
    )
    return s


def get_json(s: requests.Session, url: str, **params: Any) -> Any:
    response = s.get(url, params=params, timeout=20)
    response.raise_for_status()
    return response.json()


def percentile_99(values: list[float]) -> float:
    if not values:
        return 0.0
    if len(values) < 100:
        ordered = sorted(values)
        return ordered[max(0, math.ceil(len(ordered) * 0.99) - 1)]
    return quantiles(values, n=100, method="inclusive")[98]


def summarize_trades(trades: list[dict[str, Any]], floor: float) -> dict[str, Any]:
    notionals = [trade["price"] * trade["qty"] for trade in trades]
    threshold = max(floor, percentile_99(notionals))
    buys = sum(n for n, trade in zip(notionals, trades) if trade["side"] == "BUY")
    sells = sum(n for n, trade in zip(notionals, trades) if trade["side"] == "SELL")
    large = [
        {**trade, "notional_usd": notional}
        for trade, notional in zip(trades, notionals)
        if notional >= threshold
    ]
    large_buys = sum(x["notional_usd"] for x in large if x["side"] == "BUY")
    large_sells = sum(x["notional_usd"] for x in large if x["side"] == "SELL")
    timestamps = [trade["ts_ms"] for trade in trades]
    return {
        "trade_count": len(trades),
        "observed_from_ms": min(timestamps) if timestamps else None,
        "observed_to_ms": max(timestamps) if timestamps else None,
        "lookback_seconds": (max(timestamps) - min(timestamps)) / 1000 if len(timestamps) > 1 else 0,
        "total_notional_usd": buys + sells,
        "aggressive_buy_usd": buys,
        "aggressive_sell_usd": sells,
        "net_aggressive_usd": buys - sells,
        "buy_share": buys / (buys + sells) if buys + sells else None,
        "large_threshold_usd": threshold,
        "large_trade_count": len(large),
        "large_buy_usd": large_buys,
        "large_sell_usd": large_sells,
        "large_net_usd": large_buys - large_sells,
        "top_large_trades": sorted(large, key=lambda x: x["notional_usd"], reverse=True)[:5],
    }


def summarize_book(bids: list[list[Any]], asks: list[list[Any]]) -> dict[str, Any]:
    parsed_bids = [(float(row[0]), float(row[1])) for row in bids]
    parsed_asks = [(float(row[0]), float(row[1])) for row in asks]
    if not parsed_bids or not parsed_asks:
        raise ValueError("empty order book")
    mid = (parsed_bids[0][0] + parsed_asks[0][0]) / 2

    def depth(rows: list[tuple[float, float]], pct: float, bid: bool) -> float:
        low, high = mid * (1 - pct), mid * (1 + pct)
        return sum(price * qty for price, qty in rows if (price >= low if bid else price <= high))

    result: dict[str, Any] = {"mid": mid}
    for label, pct in (("0_5pct", 0.005), ("1pct", 0.01)):
        bid_usd = depth(parsed_bids, pct, True)
        ask_usd = depth(parsed_asks, pct, False)
        result[label] = {
            "bid_usd": bid_usd,
            "ask_usd": ask_usd,
            "imbalance": (bid_usd - ask_usd) / (bid_usd + ask_usd) if bid_usd + ask_usd else None,
        }
    return result


def binance_snapshot(s: requests.Session, symbol: str, floor: float) -> dict[str, Any]:
    raw_trades = get_json(s, "https://api.binance.com/api/v3/aggTrades", symbol=symbol, limit=1000)
    raw_book = get_json(s, "https://api.binance.com/api/v3/depth", symbol=symbol, limit=1000)
    trades = [
        {
            "price": float(row["p"]),
            "qty": float(row["q"]),
            "side": "SELL" if row["m"] else "BUY",
            "ts_ms": int(row["T"]),
        }
        for row in raw_trades
    ]
    return {
        "venue": "Binance Spot",
        "evidence": "VERIFIED",
        "trade_tape": summarize_trades(trades, floor),
        "order_book": summarize_book(raw_book["bids"], raw_book["asks"]),
    }


def okx_snapshot(s: requests.Session, instrument: str, floor: float) -> dict[str, Any]:
    raw_trades = get_json(s, "https://www.okx.com/api/v5/market/trades", instId=instrument, limit=500)["data"]
    raw_book = get_json(s, "https://www.okx.com/api/v5/market/books", instId=instrument, sz=400)["data"][0]
    trades = [
        {
            "price": float(row["px"]),
            "qty": float(row["sz"]),
            "side": row["side"].upper(),
            "ts_ms": int(row["ts"]),
        }
        for row in raw_trades
    ]
    return {
        "venue": "OKX Spot",
        "evidence": "VERIFIED",
        "trade_tape": summarize_trades(trades, floor),
        "order_book": summarize_book(raw_book["bids"], raw_book["asks"]),
    }


def spot_orderflow(s: requests.Session) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    output: dict[str, Any] = {}
    coverage: list[dict[str, Any]] = []
    for asset, cfg in ASSETS.items():
        venues: dict[str, Any] = {}
        errors: dict[str, str] = {}
        for name, loader in (
            ("binance", lambda: binance_snapshot(s, cfg["binance"], cfg["floor"])),
            ("okx", lambda: okx_snapshot(s, cfg["okx"], cfg["floor"])),
        ):
            try:
                venues[name] = loader()
            except Exception as exc:
                errors[name] = str(exc)[:240]
        preferred = "binance" if "binance" in venues else "okx" if "okx" in venues else None
        output[asset] = {"preferred": preferred, "venues": venues, "errors": errors}
        coverage.append(
            {
                "field": f"{asset} spot large trades/order book",
                "direct": "Binance Spot aggTrades + depth",
                "fallback": "OKX trades + books",
                "result": "SUCCESS" if preferred else "UNAVAILABLE",
                "evidence": "VERIFIED" if preferred else "UNAVAILABLE",
                "errors": errors,
            }
        )
    return output, coverage


def onchain_candidates(s: requests.Session, btc_mark: float | None) -> dict[str, Any]:
    rows = get_json(s, "https://mempool.space/api/mempool/recent")
    candidates = []
    for row in rows:
        btc = float(row.get("value", 0)) / 100_000_000
        candidates.append(
            {
                "txid": row.get("txid"),
                "btc": btc,
                "usd": btc * btc_mark if btc_mark else None,
                "fee_sats": row.get("fee"),
            }
        )
    candidates.sort(key=lambda x: x["btc"], reverse=True)
    return {
        "source": "mempool.space /api/mempool/recent",
        "evidence": "PROXY",
        "scope": "latest 10 unconfirmed/recent BTC transactions returned by the public endpoint",
        "count_ge_100_btc": sum(x["btc"] >= 100 for x in candidates),
        "top_candidates": candidates[:5],
        "warning": "Addresses are unlabeled. A large transaction is not an exchange flow and is not proof of buying or selling.",
    }


def strip_html(raw: str) -> str:
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def strategy_treasury(s: requests.Session) -> dict[str, Any]:
    submissions = get_json(s, f"https://data.sec.gov/submissions/CIK{STRATEGY_CIK}.json")
    recent = submissions["filings"]["recent"]
    checked = []
    fetch_errors = []
    pattern = re.compile(
        r"BTC Purchased.*?Average Purchase Price \(2\).*?Aggregate BTC Holdings.*?Average Purchase Price \(2\)\s+"
        r"([\d,]+)\s+\$\s+([\d,.]+)\s+\$\s+([\d,]+)\s+([\d,]+)\s+\$\s+([\d,.]+)\s+\$\s+([\d,]+)",
        flags=re.I | re.S,
    )
    for index, form in enumerate(recent["form"]):
        if form != "8-K":
            continue
        accession = recent["accessionNumber"][index]
        document = recent["primaryDocument"][index]
        filing_date = recent["filingDate"][index]
        accession_flat = accession.replace("-", "")
        url = f"https://www.sec.gov/Archives/edgar/data/{int(STRATEGY_CIK)}/{accession_flat}/{document}"
        checked.append({"filing_date": filing_date, "url": url})
        try:
            response = s.get(url, timeout=20)
            response.raise_for_status()
            match = pattern.search(strip_html(response.text))
        except Exception as exc:
            fetch_errors.append({"filing_date": filing_date, "url": url, "error": str(exc)[:180]})
            match = None
        if match:
            purchased, purchase_m, acquisition_avg, holdings, cost_bn, avg_cost = match.groups()
            return {
                "entity": "Strategy Inc.",
                "filing_date": filing_date,
                "source_url": url,
                "acquired_btc": int(purchased.replace(",", "")),
                "purchase_usd_m": float(purchase_m.replace(",", "")),
                "acquisition_average_usd": float(acquisition_avg.replace(",", "")),
                "holdings_btc": int(holdings.replace(",", "")),
                "aggregate_cost_usd_bn": float(cost_bn.replace(",", "")),
                "average_cost_usd": float(avg_cost.replace(",", "")),
                "evidence": "VERIFIED",
                "status": "LATEST_BITCOIN_UPDATE_FOUND",
            }
        if len(checked) >= 12:
            break
    if checked and len(fetch_errors) == len(checked):
        raise RuntimeError(f"all SEC filing document requests failed: {fetch_errors[0]['error']}")
    return {
        "entity": "Strategy Inc.",
        "status": "NO_BITCOIN_UPDATE_IN_RECENT_8K_SCAN",
        "latest_checked": checked[0] if checked else None,
        "checked_count": len(checked),
        "fetch_errors": fetch_errors,
        "evidence": "VERIFIED",
    }


def collect(now: datetime | None = None, marks: dict[str, float] | None = None) -> dict[str, Any]:
    now = now or datetime.now(BJT)
    marks = marks or {}
    s = session()
    coverage: list[dict[str, Any]] = []
    errors: dict[str, str] = {}

    spot, spot_coverage = spot_orderflow(s)
    coverage.extend(spot_coverage)

    try:
        onchain = onchain_candidates(s, marks.get("BTC"))
        coverage.append(
            {
                "field": "BTC large on-chain transfer candidates",
                "direct": "mempool.space recent transaction API",
                "fallback": "none required",
                "result": "SUCCESS",
                "evidence": "PROXY",
                "errors": {},
            }
        )
    except Exception as exc:
        errors["onchain"] = str(exc)[:240]
        onchain = {"evidence": "UNAVAILABLE", "error": errors["onchain"]}
        coverage.append(
            {
                "field": "BTC large on-chain transfer candidates",
                "direct": "mempool.space recent transaction API",
                "fallback": "none configured",
                "result": "UNAVAILABLE",
                "evidence": "UNAVAILABLE",
                "errors": {"mempool.space": errors["onchain"]},
            }
        )

    try:
        treasury = strategy_treasury(s)
        coverage.append(
            {
                "field": "public-company BTC treasury",
                "direct": "SEC EDGAR Strategy 8-K",
                "fallback": "Strategy investor relations (manual review)",
                "result": "SUCCESS",
                "evidence": "VERIFIED",
                "errors": {},
            }
        )
    except Exception as exc:
        errors["treasury"] = str(exc)[:240]
        treasury = {"evidence": "UNAVAILABLE", "error": errors["treasury"]}
        coverage.append(
            {
                "field": "public-company BTC treasury",
                "direct": "SEC EDGAR Strategy 8-K",
                "fallback": "Strategy investor relations (manual review)",
                "result": "UNAVAILABLE",
                "evidence": "UNAVAILABLE",
                "errors": {"SEC": errors["treasury"]},
            }
        )

    cex_netflow = {
        "status": "UNAVAILABLE",
        "evidence": "UNAVAILABLE",
        "reason": "Public exchange APIs do not expose wallet-labelled deposits/withdrawals. No authenticated labelled-flow provider is configured.",
        "warning": "Spot trade tape and order-book imbalance must not be described as CEX wallet netflow.",
    }
    coverage.append(
        {
            "field": "labelled CEX wallet netflow",
            "direct": "exchange public API capability check",
            "fallback": "authenticated labelled-flow provider not configured",
            "result": "UNAVAILABLE",
            "evidence": "UNAVAILABLE",
            "errors": {"reason": cex_netflow["reason"]},
        }
    )

    successful = sum(row["result"] == "SUCCESS" for row in coverage)
    return {
        "retrieved_bjt": now.isoformat(),
        "status": "SUCCESS" if successful == len(coverage) else "PARTIAL_FAILURE" if successful else "DATA_COLLECTION_FAILED",
        "spot_orderflow": spot,
        "onchain_large_transfers": onchain,
        "treasury_monitor": treasury,
        "cex_netflow": cex_netflow,
        "coverage": coverage,
        "errors": errors,
        "interpretation_guardrail": "Aggressive spot trades, visible order-book liquidity, unlabeled on-chain transfers, and labelled CEX wallet flows are four different evidence types.",
    }


def self_test() -> None:
    trades = [
        {"price": 100.0, "qty": 10.0, "side": "BUY", "ts_ms": 1_000},
        {"price": 101.0, "qty": 5.0, "side": "SELL", "ts_ms": 2_000},
    ]
    summary = summarize_trades(trades, 100)
    assert summary["aggressive_buy_usd"] == 1000
    assert summary["aggressive_sell_usd"] == 505
    assert summary["net_aggressive_usd"] == 495
    book = summarize_book([["99", "10"], ["98", "20"]], [["101", "8"], ["102", "9"]])
    assert book["mid"] == 100
    assert book["1pct"]["bid_usd"] == 990
    assert book["1pct"]["ask_usd"] == 808
    print("self-test: PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    payload = collect()
    encoded = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
        print(args.output)
    else:
        print(encoded)


if __name__ == "__main__":
    main()
