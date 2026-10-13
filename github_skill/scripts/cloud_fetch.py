from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from whale_treasury_orderflow import collect as collect_whale_treasury_orderflow

OUT = ROOT / f"live_market_detail_{datetime.now(ZoneInfo('Asia/Shanghai')):%Y%m%d}.json"
KEY_PERSON_REGISTRY = ROOT / "key_person_monitor.json"
S = requests.Session()
S.headers["User-Agent"] = "Mozilla/5.0"


def get(url, **params):
    response = S.get(url, params=params, timeout=20)
    response.raise_for_status()
    return response.json()


BINANCE_BASES = (
    "https://fapi.binance.com",
    "https://fapi1.binance.com",
    "https://fapi2.binance.com",
    "https://fapi3.binance.com",
)
BYBIT_BASE = "https://api.bybit.com"


def binance(path, **params):
    last_error = None
    for base in BINANCE_BASES:
        try:
            return get(base + path, **params)
        except requests.RequestException as error:
            last_error = error
    raise RuntimeError(f"Binance futures endpoints unavailable: {last_error}")


def bybit(path, **params):
    response = S.get(BYBIT_BASE + path, params=params, timeout=20)
    response.raise_for_status()
    payload = response.json()
    if payload.get("retCode") != 0:
        raise RuntimeError(f"Bybit request failed: {payload}")
    return payload["result"]


def yahoo(symbol):
    raw = get(
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
        interval="1d",
        range="10d",
    )["chart"]["result"][0]
    rows = [x for x in raw["indicators"]["quote"][0]["close"] if x is not None]
    last, prev = rows[-1], rows[-2]
    return {"last": last, "prev": prev, "change_pct": (last / prev - 1) * 100}


def options(currency):
    rows = get(
        "https://www.deribit.com/api/v2/public/get_book_summary_by_currency",
        currency=currency,
        kind="option",
    )["result"]
    calls = sum(float(x.get("open_interest") or 0) for x in rows if x["instrument_name"].endswith("-C"))
    puts = sum(float(x.get("open_interest") or 0) for x in rows if x["instrument_name"].endswith("-P"))
    expiries = sorted({x["instrument_name"].split("-")[1] for x in rows})
    near = expiries[0]
    nr = [x for x in rows if x["instrument_name"].split("-")[1] == near]
    nc = sum(float(x.get("open_interest") or 0) for x in nr if x["instrument_name"].endswith("-C"))
    np = sum(float(x.get("open_interest") or 0) for x in nr if x["instrument_name"].endswith("-P"))
    ranked = sorted(rows, key=lambda x: float(x.get("open_interest") or 0), reverse=True)[:12]
    return {
        "all_pc": puts / calls if calls else None,
        "near_pc": np / nc if nc else None,
        "near_expiry": near,
        "top_strikes": [
            {"name": x["instrument_name"], "oi": float(x.get("open_interest") or 0)}
            for x in ranked
        ],
    }


def key_person_monitor(now):
    """Collect secondary-source candidates; final stance changes still need source review."""
    registry = json.loads(KEY_PERSON_REGISTRY.read_text(encoding="utf-8"))
    candidates, failures = [], []
    for person in registry["people"]:
        query = person["query"]
        try:
            response = S.get(
                "https://news.google.com/rss/search",
                params={"q": query, "hl": "en-US", "gl": "US", "ceid": "US:en"},
                timeout=20,
            )
            response.raise_for_status()
            root = ET.fromstring(response.content)
            items = root.findall("./channel/item")[:3]
            for item in items:
                published = item.findtext("pubDate")
                candidates.append(
                    {
                        "person": person["name"],
                        "group": person["group"],
                        "title": item.findtext("title"),
                        "url": item.findtext("link"),
                        "publisher": item.findtext("source"),
                        "published": published,
                        "evidence": "SECONDARY_CANDIDATE",
                    }
                )
        except Exception as exc:
            failures.append({"person": person["name"], "error": str(exc)[:180]})

    return {
        "cutoff_bjt": now.isoformat(),
        "registry_version": registry["version"],
        "covered_people": [person["name"] for person in registry["people"]],
        "candidate_count": len(candidates),
        "candidates": candidates,
        "validated_updates": [],
        "scan_status": "SUCCESS" if not failures else "PARTIAL_FAILURE",
        "failures": failures,
        "note": "Candidates are secondary-source leads only. A daily report may call a view new or changed only after manual primary/credible-source verification.",
    }


def asset_binance(symbol):
    ticker = binance("/fapi/v1/ticker/24hr", symbol=symbol)
    premium = binance("/fapi/v1/premiumIndex", symbol=symbol)
    funding = binance("/fapi/v1/fundingRate", symbol=symbol, limit=1)[0]
    taker = binance("/futures/data/takerlongshortRatio", symbol=symbol, period="1h", limit=3)
    oi = binance("/futures/data/openInterestHist", symbol=symbol, period="1d", limit=6)
    klines = binance("/fapi/v1/klines", symbol=symbol, interval="1h", limit=121)
    return {
        "mark": float(premium["markPrice"]),
        "change24": float(ticker["priceChangePercent"]),
        "high24": float(ticker["highPrice"]),
        "low24": float(ticker["lowPrice"]),
        "funding": float(funding["fundingRate"]) * 100,
        "taker_last3": [float(x["buySellRatio"]) for x in taker],
        "oi_5d": [{"value": float(x["sumOpenInterestValue"])} for x in oi],
        "oi_last": float(oi[-1]["sumOpenInterestValue"]),
        "oi24_pct": (float(oi[-1]["sumOpenInterestValue"]) / float(oi[-2]["sumOpenInterestValue"]) - 1) * 100,
        "klines": klines,
        "klines15m": binance("/fapi/v1/klines", symbol=symbol, interval="15m", limit=32),
        # The turning-point Shadow overlay needs mature point-in-time history.
        # Keep the current incomplete bar in the payload; consumers exclude it.
        "klines4h": binance("/fapi/v1/klines", symbol=symbol, interval="4h", limit=1500),
        "klines1d": binance("/fapi/v1/klines", symbol=symbol, interval="1d", limit=500),
    }


def bybit_klines(symbol, interval, limit):
    rows = bybit("/v5/market/kline", category="linear", symbol=symbol, interval=interval, limit=min(limit, 1000))["list"]
    rows = sorted(rows, key=lambda row: int(row[0]))
    return [[int(row[0]), row[1], row[2], row[3], row[4], row[5], row[6]] for row in rows]


def asset_bybit(symbol):
    ticker = bybit("/v5/market/tickers", category="linear", symbol=symbol)["list"][0]
    funding = bybit("/v5/market/funding/history", category="linear", symbol=symbol, limit=1)["list"]
    oi = bybit("/v5/market/open-interest", category="linear", symbol=symbol, intervalTime="1d", limit=6)["list"]
    ratio = bybit("/v5/market/account-ratio", category="linear", symbol=symbol, period="1h", limit=3)["list"]
    mark = float(ticker.get("markPrice") or ticker["lastPrice"])
    oi_rows = sorted(oi, key=lambda row: int(row["timestamp"]))
    oi_values = [float(row["openInterest"]) * mark for row in oi_rows]
    taker_values = []
    for row in sorted(ratio, key=lambda row: int(row["timestamp"])):
        buy = float(row.get("buyRatio") or 0.5)
        sell = float(row.get("sellRatio") or 0.5)
        taker_values.append(buy / sell if sell else 1.0)
    if len(taker_values) < 3:
        taker_values = [1.0, 1.0, 1.0]
    return {
        "mark": mark,
        "change24": float(ticker.get("price24hPcnt") or 0) * 100,
        "high24": float(ticker.get("highPrice24h") or mark),
        "low24": float(ticker.get("lowPrice24h") or mark),
        "funding": float(funding[0].get("fundingRate") or 0) * 100 if funding else 0.0,
        "taker_last3": taker_values[-3:],
        "oi_5d": [{"value": value} for value in oi_values],
        "oi_last": oi_values[-1] if oi_values else 0.0,
        "oi24_pct": (oi_values[-1] / oi_values[-2] - 1) * 100 if len(oi_values) >= 2 and oi_values[-2] else 0.0,
        "klines": bybit_klines(symbol, "60", 121),
        "klines15m": bybit_klines(symbol, "15", 32),
        "klines4h": bybit_klines(symbol, "240", 1000),
        "klines1d": bybit_klines(symbol, "D", 500),
        "source": "BYBIT_PUBLIC_DERIVATIVES_FALLBACK",
    }


def asset(symbol):
    try:
        return asset_binance(symbol)
    except Exception as error:
        print(f"Binance unavailable for {symbol}; using Bybit public fallback: {error}")
        return asset_bybit(symbol)


def main():
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    symbols = {"BTC": "BTCUSDT", "ETH": "ETHUSDT", "SOL": "SOLUSDT", "UNI": "UNIUSDT", "AVAX": "AVAXUSDT", "LINK": "LINKUSDT", "XRP": "XRPUSDT", "DOGE": "DOGEUSDT"}
    derivatives = {name: asset(symbol) for name, symbol in symbols.items()}
    try:
        depth = binance("/fapi/v1/depth", symbol="BTCUSDT", limit=20)
    except Exception:
        orderbook = bybit("/v5/market/orderbook", category="linear", symbol="BTCUSDT", limit=50)
        depth = {"bids": orderbook.get("b", []), "asks": orderbook.get("a", [])}
    stablecoins = get("https://stablecoins.llama.fi/stablecoins")
    whale_treasury_orderflow = collect_whale_treasury_orderflow(
        now,
        {asset: derivatives[asset]["mark"] for asset in ("BTC", "ETH", "SOL")},
    )
    macro_symbols = {"S&P 500": "%5EGSPC", "Nasdaq": "%5EIXIC", "DXY": "DX-Y.NYB", "US10Y": "%5ETNX", "Gold": "GC%3DF", "WTI": "CL%3DF"}
    payload = {
        "retrieved_bjt": now.isoformat(),
        "derivatives": derivatives,
        "depth_btc": {"bids": depth["bids"][:10], "asks": depth["asks"][:10]},
        "stablecoins": {
            "total_usd": sum(
                float(item.get("circulating", {}).get("peggedUSD", 0))
                for item in stablecoins["peggedAssets"]
            )
        },
        "macro": {name: yahoo(symbol) for name, symbol in macro_symbols.items()},
        "options": {"BTC": options("BTC"), "ETH": options("ETH")},
        "key_person_monitor": key_person_monitor(now),
        "whale_treasury_orderflow": whale_treasury_orderflow,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
