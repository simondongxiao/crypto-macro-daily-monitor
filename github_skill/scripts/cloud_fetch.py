from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
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


def iso_ms(value: object | None) -> str | None:
    if value in (None, ""):
        return None
    try:
        return datetime.fromtimestamp(float(value) / 1000, tz=timezone.utc).astimezone(ZoneInfo("Asia/Shanghai")).isoformat()
    except (TypeError, ValueError, OverflowError):
        return None


def field_audit(source: str, captured_at: str, data_timestamp: str | None, *, fallback: bool = False, estimated: bool = False, max_age_seconds: int | None = None, note: str = "") -> dict[str, object]:
    stale = None
    timestamp_anomaly = None
    if data_timestamp and max_age_seconds is not None:
        try:
            age = (datetime.fromisoformat(captured_at) - datetime.fromisoformat(data_timestamp)).total_seconds()
            stale = age > max_age_seconds
            if age < -60:
                timestamp_anomaly = "FUTURE_TIMESTAMP_OR_NEXT_SETTLEMENT"
        except ValueError:
            stale = None
    return {
        "source": source,
        "captured_at": captured_at,
        "data_timestamp": data_timestamp,
        "success": True,
        "fallback": fallback,
        "estimated_or_derived": estimated,
        "stale": stale,
        "timestamp_anomaly": timestamp_anomaly,
        "note": note,
    }


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
BYBIT_BASE = "https://api.bytick.com"
OKX_BASE = "https://www.okx.com"


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


def okx(path, **params):
    response = S.get(OKX_BASE + path, params=params, timeout=20)
    response.raise_for_status()
    payload = response.json()
    if payload.get("code") != "0":
        raise RuntimeError(f"OKX request failed: {payload}")
    return payload["data"]


def yahoo(symbol):
    captured_at = datetime.now(ZoneInfo("Asia/Shanghai")).isoformat()
    raw = get(
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
        interval="1d",
        range="10d",
    )["chart"]["result"][0]
    timestamps = raw.get("timestamp", [])
    rows = [x for x in raw["indicators"]["quote"][0]["close"] if x is not None]
    last, prev = rows[-1], rows[-2]
    data_timestamp = iso_ms(timestamps[-1] * 1000) if timestamps else None
    return {
        "last": last,
        "prev": prev,
        "change_pct": (last / prev - 1) * 100,
        "_provenance": field_audit("Yahoo Finance chart API", captured_at, data_timestamp, max_age_seconds=3 * 86400, note="Latest market close; weekend/holiday staleness is expected."),
    }


def options(currency):
    captured_at = datetime.now(ZoneInfo("Asia/Shanghai")).isoformat()
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
        "_provenance": field_audit("Deribit public options API", captured_at, None, max_age_seconds=900, note="The response has no single universal snapshot timestamp; retrieval time is recorded."),
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


def asset_binance(symbol, captured_at: str):
    ticker = binance("/fapi/v1/ticker/24hr", symbol=symbol)
    premium = binance("/fapi/v1/premiumIndex", symbol=symbol)
    funding = binance("/fapi/v1/fundingRate", symbol=symbol, limit=1)[0]
    taker = binance("/futures/data/takerlongshortRatio", symbol=symbol, period="1h", limit=3)
    oi = binance("/futures/data/openInterestHist", symbol=symbol, period="1d", limit=6)
    klines = binance("/fapi/v1/klines", symbol=symbol, interval="1h", limit=121)
    source = "Binance USDⓈ-M public API"
    mark_ts = iso_ms(premium.get("time") or ticker.get("closeTime"))
    funding_ts = iso_ms(funding.get("fundingTime"))
    oi_ts = iso_ms(oi[-1].get("timestamp")) if oi else None
    taker_ts = iso_ms(taker[-1].get("timestamp")) if taker else None
    volume_ts = iso_ms(ticker.get("closeTime"))
    closed_kline_ts = iso_ms(klines[-2][6]) if len(klines) >= 2 else None
    return {
        "mark": float(premium["markPrice"]),
        "change24": float(ticker["priceChangePercent"]),
        "high24": float(ticker["highPrice"]),
        "low24": float(ticker["lowPrice"]),
        "volume24h_quote": float(ticker.get("quoteVolume") or 0),
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
        "source": "BINANCE_USDM_DIRECT",
        "_provenance": {
            "mark": field_audit(source, captured_at, mark_ts, max_age_seconds=300),
            "funding": field_audit(source, captured_at, funding_ts, max_age_seconds=2 * 3600),
            "oi": field_audit(source, captured_at, oi_ts, max_age_seconds=2 * 86400),
            "taker": field_audit(source, captured_at, taker_ts, max_age_seconds=2 * 3600),
            "volume": field_audit(source, captured_at, volume_ts, max_age_seconds=2 * 86400),
            "klines": field_audit(source, captured_at, closed_kline_ts, max_age_seconds=2 * 3600, note="Uses the last completed 1h candle for the timestamp."),
        },
    }


def bybit_klines(symbol, interval, limit):
    rows = bybit("/v5/market/kline", category="linear", symbol=symbol, interval=interval, limit=min(limit, 1000))["list"]
    rows = sorted(rows, key=lambda row: int(row[0]))
    return [[int(row[0]), row[1], row[2], row[3], row[4], row[5], row[6]] for row in rows]


def asset_bybit(symbol, captured_at: str):
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
    source = "Bybit public derivatives API"
    mark_ts = iso_ms(ticker.get("ts"))
    funding_ts = iso_ms(funding[0].get("fundingRateTimestamp")) if funding else None
    oi_ts = iso_ms(oi_rows[-1].get("timestamp")) if oi_rows else None
    taker_ts = iso_ms(sorted(ratio, key=lambda row: int(row["timestamp"]))[-1].get("timestamp")) if ratio else None
    # Bybit kline rows are [start_ms, open, high, low, close, volume, turnover].
    # The last completed candle timestamp is the first column, not turnover.
    closed_kline_ts = iso_ms(bybit_klines(symbol, "60", 121)[-2][0])
    return {
        "mark": mark,
        "change24": float(ticker.get("price24hPcnt") or 0) * 100,
        "high24": float(ticker.get("highPrice24h") or mark),
        "low24": float(ticker.get("lowPrice24h") or mark),
        "volume24h_quote": float(ticker.get("turnover24h") or 0),
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
        "_provenance": {
            "mark": field_audit(source, captured_at, mark_ts, fallback=True, max_age_seconds=300),
            "funding": field_audit(source, captured_at, funding_ts, fallback=True, max_age_seconds=2 * 3600),
            "oi": field_audit(source, captured_at, oi_ts, fallback=True, max_age_seconds=2 * 86400),
            "taker": field_audit(source, captured_at, taker_ts, fallback=True, max_age_seconds=2 * 3600),
            "volume": field_audit(source, captured_at, mark_ts, fallback=True, estimated=True, max_age_seconds=2 * 86400),
            "klines": field_audit(source, captured_at, closed_kline_ts, fallback=True, max_age_seconds=2 * 3600),
        },
    }


def okx_klines(inst_id, bar, limit):
    rows = okx("/api/v5/market/candles", instId=inst_id, bar=bar, limit=min(limit, 100))[0:limit]
    rows = sorted(rows, key=lambda row: int(row[0]))
    return [[int(row[0]), row[1], row[2], row[3], row[4], row[5], row[6]] for row in rows]


def asset_okx(symbol, captured_at: str):
    inst_id = symbol.replace("USDT", "-USDT-SWAP")
    ticker = okx("/api/v5/market/ticker", instId=inst_id)[0]
    funding = okx("/api/v5/public/funding-rate", instId=inst_id)[0]
    oi = okx("/api/v5/public/open-interest", instType="SWAP", instId=inst_id)[0]
    trades = okx("/api/v5/market/trades", instId=inst_id, limit=100)
    buy_size = sum(float(row["sz"]) for row in trades if row.get("side") == "buy")
    sell_size = sum(float(row["sz"]) for row in trades if row.get("side") == "sell")
    taker = buy_size / sell_size if sell_size else 1.0
    mark = float(ticker["last"])
    open24 = float(ticker.get("open24h") or mark)
    open_interest = float(oi.get("oiCcy") or oi.get("oi") or 0) * mark
    source = "OKX public SWAP API"
    mark_ts = iso_ms(ticker.get("ts"))
    funding_ts = iso_ms(funding.get("fundingTime"))
    oi_ts = iso_ms(oi.get("ts"))
    # OKX candle rows are [ts, open, high, low, close, vol, volCcy, ...].
    # Column 6 is volume in quote currency; using it as a timestamp creates a
    # false 1970 stale-data audit and can make a fresh profile look invalid.
    closed_kline_ts = iso_ms(okx_klines(inst_id, "1H", 100)[-2][0])
    return {
        "mark": mark,
        "change24": (mark / open24 - 1) * 100 if open24 else 0.0,
        "high24": float(ticker.get("high24h") or mark),
        "low24": float(ticker.get("low24h") or mark),
        "volume24h_quote": float(ticker.get("volCcy24h") or 0),
        "funding": float(funding.get("fundingRate") or 0) * 100,
        "taker_last3": [taker, taker, taker],
        "oi_5d": [{"value": open_interest}],
        "oi_last": open_interest,
        "oi24_pct": 0.0,
        "klines": okx_klines(inst_id, "1H", 100),
        "klines15m": okx_klines(inst_id, "15m", 32),
        "klines4h": okx_klines(inst_id, "4H", 100),
        "klines1d": okx_klines(inst_id, "1Dutc", 100),
        "source": "OKX_PUBLIC_DERIVATIVES_FALLBACK",
        "_provenance": {
            "mark": field_audit(source, captured_at, mark_ts, fallback=True, max_age_seconds=300),
            "funding": field_audit(source, captured_at, funding_ts, fallback=True, max_age_seconds=2 * 3600),
            "oi": field_audit(source, captured_at, oi_ts, fallback=True, max_age_seconds=2 * 86400),
            "taker": field_audit(source, captured_at, mark_ts, fallback=True, estimated=True, max_age_seconds=300, note="Derived from the latest public trades snapshot; no native historical taker series."),
            "volume": field_audit(source, captured_at, mark_ts, fallback=True, estimated=True, max_age_seconds=2 * 86400),
            "klines": field_audit(source, captured_at, closed_kline_ts, fallback=True, max_age_seconds=2 * 3600),
        },
    }


def asset(symbol):
    captured_at = datetime.now(ZoneInfo("Asia/Shanghai")).isoformat()
    try:
        return asset_binance(symbol, captured_at)
    except Exception as error:
        print(f"Binance unavailable for {symbol}; trying Bybit public fallback: {error}")
        try:
            return asset_bybit(symbol, captured_at)
        except Exception as bybit_error:
            print(f"Bybit unavailable for {symbol}; using OKX public fallback: {bybit_error}")
            return asset_okx(symbol, captured_at)


def build_source_audit(now: datetime, derivatives: dict[str, dict], macro: dict[str, dict], options_payload: dict[str, dict], stablecoins: dict, depth_source: str, whale: dict) -> dict[str, object]:
    captured_at = now.isoformat()
    fields: dict[str, object] = {}
    for asset_name in ("BTC", "ETH", "SOL"):
        item = derivatives.get(asset_name, {})
        provenance = item.get("_provenance", {})
        for field_name in ("mark", "funding", "oi", "taker", "volume", "klines"):
            fields[f"derivatives.{asset_name}.{field_name}"] = provenance.get(field_name) or {
                "source": item.get("source", "UNKNOWN"),
                "captured_at": captured_at,
                "data_timestamp": None,
                "success": False,
                "fallback": "FALLBACK" in str(item.get("source", "")),
                "estimated_or_derived": True,
                "stale": None,
                "note": "Field-level provenance was not returned by the source adapter.",
            }
    for name, item in macro.items():
        fields[f"macro.{name}"] = item.get("_provenance") or {
            "source": "Yahoo Finance chart API",
            "captured_at": captured_at,
            "data_timestamp": None,
            "success": False,
            "fallback": False,
            "estimated_or_derived": False,
            "stale": None,
            "note": "No field-level provenance returned.",
        }
    for name, item in options_payload.items():
        fields[f"options.{name}"] = item.get("_provenance") or {
            "source": "Deribit public options API",
            "captured_at": captured_at,
            "data_timestamp": None,
            "success": False,
            "fallback": False,
            "estimated_or_derived": False,
            "stale": None,
            "note": "No field-level provenance returned.",
        }
    if stablecoins.get("_unavailable"):
        fields["stablecoins.total_usd"] = {
            "source": "DefiLlama stablecoins API",
            "captured_at": captured_at,
            "data_timestamp": None,
            "success": False,
            "fallback": False,
            "estimated_or_derived": False,
            "stale": None,
            "timestamp_anomaly": None,
            "note": f"Unavailable this run: {stablecoins.get('_error', 'unknown error')}",
        }
    else:
        fields["stablecoins.total_usd"] = field_audit(
            "DefiLlama stablecoins API", captured_at, None, max_age_seconds=86400,
            note="Aggregate is derived by summing peggedAssets; API response has no single aggregate timestamp.",
        )
    fields["depth_btc"] = field_audit(depth_source, captured_at, None, max_age_seconds=300, note="Order-book snapshot retrieval time is the freshness timestamp.")
    fields["whale_treasury_orderflow"] = field_audit(
        "Binance/OKX spot + mempool.space + SEC EDGAR adapters",
        whale.get("retrieved_bjt", captured_at),
        whale.get("retrieved_bjt"),
        estimated=whale.get("status") != "SUCCESS",
        note="Subfields retain their own venue/evidence coverage; wallet-labelled CEX netflow may be unavailable.",
    )
    success = sum(bool(value.get("success")) for value in fields.values() if isinstance(value, dict))
    stale = sum(value.get("stale") is True for value in fields.values() if isinstance(value, dict))
    estimated = sum(bool(value.get("estimated_or_derived")) for value in fields.values() if isinstance(value, dict))
    return {
        "generated_at": captured_at,
        "fields": fields,
        "summary": {"field_count": len(fields), "success_count": success, "stale_count": stale, "estimated_or_derived_count": estimated},
        "guardrail": "A successful report only means the document build completed; field-level availability and freshness are recorded separately.",
    }


def main():
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    symbols = {"BTC": "BTCUSDT", "ETH": "ETHUSDT", "SOL": "SOLUSDT", "UNI": "UNIUSDT", "AVAX": "AVAXUSDT", "LINK": "LINKUSDT", "XRP": "XRPUSDT", "DOGE": "DOGEUSDT"}
    derivatives = {name: asset(symbol) for name, symbol in symbols.items()}
    depth_source = "Binance USDⓈ-M order-book API"
    try:
        depth = binance("/fapi/v1/depth", symbol="BTCUSDT", limit=20)
    except Exception:
        try:
            orderbook = bybit("/v5/market/orderbook", category="linear", symbol="BTCUSDT", limit=50)
            depth = {"bids": orderbook.get("b", []), "asks": orderbook.get("a", [])}
            depth_source = "Bybit public derivatives order-book API"
        except Exception:
            orderbook = okx("/api/v5/market/books", instId="BTC-USDT-SWAP", sz=20)[0]
            depth = {"bids": orderbook.get("bids", []), "asks": orderbook.get("asks", [])}
            depth_source = "OKX public SWAP order-book API"
    try:
        stablecoins = get("https://stablecoins.llama.fi/stablecoins")
    except Exception as error:
        # A transient stablecoin endpoint failure must not discard the rest of
        # the fresh market snapshot. Keep the field explicitly unavailable so
        # the report and audit cannot mistake an old or estimated value for
        # current data.
        stablecoins = {
            "peggedAssets": [],
            "_unavailable": True,
            "_error": str(error)[:240],
        }
    whale_treasury_orderflow = collect_whale_treasury_orderflow(
        now,
        {asset: derivatives[asset]["mark"] for asset in ("BTC", "ETH", "SOL")},
    )
    macro_symbols = {"S&P 500": "%5EGSPC", "Nasdaq": "%5EIXIC", "DXY": "DX-Y.NYB", "US10Y": "%5ETNX", "Gold": "GC%3DF", "WTI": "CL%3DF"}
    macro = {name: yahoo(symbol) for name, symbol in macro_symbols.items()}
    options_payload = {"BTC": options("BTC"), "ETH": options("ETH")}
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
        "macro": macro,
        "options": options_payload,
        "key_person_monitor": key_person_monitor(now),
        "whale_treasury_orderflow": whale_treasury_orderflow,
    }
    payload["data_source_audit"] = build_source_audit(now, derivatives, macro, options_payload, stablecoins, depth_source, whale_treasury_orderflow)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
