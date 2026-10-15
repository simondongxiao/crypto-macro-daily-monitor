#!/usr/bin/env python3
"""Poll prices, record an auditable decision, and send only real condition alerts."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import requests

BJT = ZoneInfo("Asia/Shanghai")
BINANCE_URLS = (
    "https://api.binance.com/api/v3/ticker/price",
    "https://api1.binance.com/api/v3/ticker/price",
    "https://api2.binance.com/api/v3/ticker/price",
    "https://api3.binance.com/api/v3/ticker/price",
    "https://api4.binance.com/api/v3/ticker/price",
)
COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
OKX_URL = "https://www.okx.com/api/v5/market/tickers"
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
ASSET_NAMES = {"BTCUSDT": "BTC", "ETHUSDT": "ETH", "SOLUSDT": "SOL"}
MAX_QUOTE_AGE_SECONDS = 300
MAX_CROSS_SOURCE_DEVIATION_PCT = 1.0


def load_conditions(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload.get("assets"), dict):
        raise ValueError("active_conditions.json must contain an assets object")
    for symbol in SYMBOLS:
        item = payload["assets"].get(symbol)
        if not isinstance(item, dict):
            raise ValueError(f"missing assets.{symbol}")
        for side in ("long", "short"):
            zone = item.get(f"{side}_zone")
            if not isinstance(zone, list) or len(zone) not in (0, 2):
                raise ValueError(f"{symbol}.{side}_zone must be [] or [min, max]")
            if len(zone) == 2 and not all(isinstance(x, (int, float)) for x in zone):
                raise ValueError(f"{symbol}.{side}_zone must contain numeric bounds")
            if len(zone) == 2 and zone[0] > zone[1]:
                raise ValueError(f"{symbol}.{side}_zone has min > max")
            if not isinstance(item.get(f"alerted_{side}"), bool):
                raise ValueError(f"{symbol}.alerted_{side} must be boolean")
    if not isinstance(payload.get("sent_alerts", {}), dict):
        raise ValueError("sent_alerts must be an object when present")
    return payload


def _quote_record(source: str, captured_at: datetime, prices: dict[str, float], data_timestamps: dict[str, str | None]) -> dict[str, Any]:
    return {"source": source, "captured_at": captured_at.isoformat(), "prices": prices, "data_timestamps": data_timestamps}


def fetch_prices(session: requests.Session, captured_at: datetime) -> tuple[dict[str, float], str, list[str], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    failures: list[str] = []
    quotes: dict[str, dict[str, Any]] = {}
    params = {"symbols": json.dumps(list(SYMBOLS), separators=(",", ":"))}
    for endpoint in BINANCE_URLS:
        try:
            response = session.get(endpoint, params=params, timeout=15)
            response.raise_for_status()
            rows = response.json()
            if not isinstance(rows, list):
                raise RuntimeError(f"non-list response: {rows}")
            prices = {row["symbol"]: float(row["price"]) for row in rows}
            missing = [symbol for symbol in SYMBOLS if symbol not in prices]
            if not missing:
                quotes["Binance Spot ticker"] = _quote_record("Binance Spot ticker", captured_at, prices, {symbol: None for symbol in SYMBOLS})
                break
            failures.append(f"{endpoint}: missing {','.join(missing)}")
        except (requests.RequestException, KeyError, TypeError, ValueError, RuntimeError) as error:
            failures.append(f"{endpoint}: {error}")

    try:
        response = session.get(COINGECKO_URL, params={"ids": "bitcoin,ethereum,solana", "vs_currencies": "usd", "include_last_updated_at": "true"}, timeout=15)
        response.raise_for_status()
        rows = response.json()
        prices = {
            "BTCUSDT": float(rows["bitcoin"]["usd"]),
            "ETHUSDT": float(rows["ethereum"]["usd"]),
            "SOLUSDT": float(rows["solana"]["usd"]),
        }
        timestamps = {
            "BTCUSDT": datetime.fromtimestamp(float(rows["bitcoin"].get("last_updated_at", 0)), tz=BJT).isoformat() if rows["bitcoin"].get("last_updated_at") else None,
            "ETHUSDT": datetime.fromtimestamp(float(rows["ethereum"].get("last_updated_at", 0)), tz=BJT).isoformat() if rows["ethereum"].get("last_updated_at") else None,
            "SOLUSDT": datetime.fromtimestamp(float(rows["solana"].get("last_updated_at", 0)), tz=BJT).isoformat() if rows["solana"].get("last_updated_at") else None,
        }
        quotes["CoinGecko"] = _quote_record("CoinGecko", captured_at, prices, timestamps)
    except (requests.RequestException, KeyError, TypeError, ValueError) as error:
        failures.append(f"{COINGECKO_URL}: {error}")

    try:
        response = session.get(OKX_URL, params=[("instType", "SWAP"), ("instId", "BTC-USDT-SWAP"), ("instId", "ETH-USDT-SWAP"), ("instId", "SOL-USDT-SWAP")], timeout=15)
        response.raise_for_status()
        rows = response.json()["data"]
        by_symbol = {row["instId"].replace("-USDT-SWAP", "USDT"): row for row in rows}
        prices = {symbol: float(by_symbol[symbol]["last"]) for symbol in SYMBOLS}
        timestamps = {symbol: datetime.fromtimestamp(float(by_symbol[symbol]["ts"]) / 1000, tz=BJT).isoformat() if by_symbol[symbol].get("ts") else None for symbol in SYMBOLS}
        quotes["OKX Swap ticker"] = _quote_record("OKX Swap ticker", captured_at, prices, timestamps)
    except (requests.RequestException, KeyError, TypeError, ValueError) as error:
        failures.append(f"{OKX_URL}: {error}")

    if not quotes:
        raise RuntimeError(f"Binance, CoinGecko and OKX public endpoints failed: {failures}")
    selected_source = "Binance Spot ticker" if "Binance Spot ticker" in quotes else "CoinGecko" if "CoinGecko" in quotes else "OKX Swap ticker"
    selected = quotes[selected_source]["prices"]
    validity: dict[str, dict[str, Any]] = {}
    for symbol in SYMBOLS:
        values = [float(quote["prices"][symbol]) for quote in quotes.values() if symbol in quote["prices"]]
        source = quotes[selected_source]
        data_timestamp = source["data_timestamps"].get(symbol)
        timestamp = datetime.fromisoformat(data_timestamp) if data_timestamp else captured_at
        age_seconds = max(0.0, (captured_at - timestamp).total_seconds())
        deviation = (max(values) / min(values) - 1) * 100 if len(values) >= 2 and min(values) else None
        reasons = []
        if age_seconds > MAX_QUOTE_AGE_SECONDS:
            reasons.append("STALE_QUOTE")
        if len(values) < 2:
            reasons.append("INSUFFICIENT_INDEPENDENT_SOURCES")
        if deviation is not None and deviation > MAX_CROSS_SOURCE_DEVIATION_PCT:
            reasons.append("CROSS_SOURCE_DEVIATION")
        validity[symbol] = {"valid": not reasons, "age_seconds": round(age_seconds, 2), "cross_source_deviation_pct": round(deviation, 4) if deviation is not None else None, "reason": ";".join(reasons) if reasons else "OK"}
    return selected, selected_source, failures, quotes, validity


def signal_text(side: str) -> str:
    if side == "long":
        return "进入多头观察区后，15m/30m 先确认扫低收回、形成 HL，且 Taker/CVD 不再恶化；提醒不等于直接下单。"
    return "进入空头观察区后，15m/30m 先确认冲高失败、跌回关键区下方、形成 LH，且 Taker/CVD 没有重新转强；提醒不等于直接下单。"


def send_feishu(session: requests.Session, webhook: str, symbol: str, side: str, price: float, zone: list[float], price_source: str) -> dict[str, Any]:
    direction = "做多观察区" if side == "long" else "做空观察区"
    card = {
        "config": {"wide_screen_mode": True},
        "header": {"template": "green" if side == "long" else "red", "title": {"tag": "plain_text", "content": f"Crypto 条件区触发：{ASSET_NAMES[symbol]} {direction}"}},
        "elements": [
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**品种：** {ASSET_NAMES[symbol]} (`{symbol}`)\n**实时价格：** `{price:,.8f}`\n**触发区间：** `{zone[0]:,.8f} - {zone[1]:,.8f}`"}},
            {"tag": "hr"},
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**微观确认：** {signal_text(side)}"}},
            {"tag": "note", "elements": [{"tag": "plain_text", "content": f"报价源：{price_source}；已通过独立源偏差与过期检查。请以 Daily Review 的 SL、TP、Max Entry 和失效条件为准。"}]},
        ],
    }
    response = session.post(webhook, json={"msg_type": "interactive", "card": card}, timeout=15)
    response.raise_for_status()
    try:
        body = response.json()
    except ValueError as error:
        raise RuntimeError(f"Feishu returned non-JSON response: HTTP {response.status_code}") from error
    if not isinstance(body, dict) or "code" not in body:
        raise RuntimeError(f"Feishu response missing code: {body}")
    if body.get("code") != 0:
        raise RuntimeError(f"Feishu rejected card: {body}")
    return body


def atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def write_audit(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=os.environ.get("ACTIVE_CONDITIONS_PATH", "config/active_conditions.json"))
    parser.add_argument("--webhook", default=os.environ.get("FEISHU_WEBHOOK_URL"))
    parser.add_argument("--dry-run", action="store_true", help="fetch and evaluate prices without sending or writing alerts")
    args = parser.parse_args()

    now = datetime.now(BJT)
    config_path = Path(args.config)
    audit_path = Path(os.environ.get("MONITOR_AUDIT_PATH", f"monitor_logs/price_monitor_{now:%Y%m%d}.jsonl"))
    payload = load_conditions(config_path)
    session = requests.Session()
    session.headers["User-Agent"] = "crypto-macro-daily-review-price-monitor/1.1"
    prices, price_source, source_failures, source_quotes, price_validity = fetch_prices(session, now)
    today = now.date().isoformat()
    evaluations: list[dict[str, Any]] = []
    notifications: list[dict[str, Any]] = []
    stale = payload.get("date") != today
    notification_failed = False

    print(f"MONITOR_RUN query_time_bjt={now.isoformat()} config_date={payload.get('date')} today={today}")
    print(f"PRICE_SOURCE source={price_source}")
    print(f"PRICE BTC={prices['BTCUSDT']} ETH={prices['ETHUSDT']} SOL={prices['SOLUSDT']}")
    for source, quote in source_quotes.items():
        print(f"QUOTE_SOURCE source={source} captured_at={quote['captured_at']} data_timestamps={quote['data_timestamps']}")
    for symbol, validity in price_validity.items():
        print(f"QUOTE_VALIDITY {symbol} valid={validity['valid']} age_seconds={validity['age_seconds']} cross_source_deviation_pct={validity['cross_source_deviation_pct']} reason={validity['reason']}")
    if source_failures:
        print(f"PRICE_SOURCE_FALLBACK failures={source_failures}")

    changed = False
    sent_alerts = payload.setdefault("sent_alerts", {})
    for symbol in SYMBOLS:
        item = payload["assets"][symbol]
        print(f"ZONE {symbol} long={item['long_zone']} short={item['short_zone']} alerted_long={item['alerted_long']} alerted_short={item['alerted_short']}")
        for side in ("long", "short"):
            zone = item[f"{side}_zone"]
            flag = f"alerted_{side}"
            alert_id = f"{today}:{symbol}:{side}:{','.join(map(str, zone))}"
            if stale:
                reason = "STALE_CONFIG_DATE"
            elif not price_validity[symbol]["valid"]:
                reason = f"DATA_INVALID:{price_validity[symbol]['reason']}"
            elif not zone:
                reason = "NO_ZONE"
            elif item[flag] or alert_id in sent_alerts:
                reason = "ALREADY_ALERTED"
            elif not (zone[0] <= prices[symbol] <= zone[1]):
                reason = "OUTSIDE_ZONE"
            else:
                reason = "TRIGGERED"
            evaluation = {"symbol": symbol, "side": side, "price": prices[symbol], "zone": zone, "alert_id": alert_id, "reason": reason, "quote_validity": price_validity[symbol]}
            evaluations.append(evaluation)
            if reason != "TRIGGERED":
                print(f"NO_TRIGGER {symbol} {side} reason={reason}")
                continue
            if args.dry_run:
                print(f"DRY_RUN_TRIGGER {symbol} {side} price={prices[symbol]} zone={zone}")
                continue
            if not args.webhook:
                notifications.append({"symbol": symbol, "side": side, "status": "NOTIFICATION_FAILED", "reason": "WEBHOOK_MISSING"})
                notification_failed = True
                print(f"NOTIFICATION_FAILED {symbol} {side} reason=WEBHOOK_MISSING")
                continue
            try:
                body = send_feishu(session, args.webhook, symbol, side, prices[symbol], zone, price_source)
                item[flag] = True
                sent_alerts[alert_id] = {"status": "ACCEPTED", "sent_at_bjt": now.isoformat(), "source": price_source}
                atomic_write(config_path, payload)
                changed = True
                notifications.append({"symbol": symbol, "side": side, "status": "SENT_AND_ACCEPTED", "feishu_code": body.get("code")})
                print(f"NOTIFICATION_SENT {symbol} {side} price={prices[symbol]} feishu_code={body.get('code')}")
            except Exception as error:
                notifications.append({"symbol": symbol, "side": side, "status": "NOTIFICATION_FAILED", "reason": str(error)[:300]})
                print(f"NOTIFICATION_FAILED {symbol} {side} reason={error}")
                notification_failed = True

    status = "STALE_CONFIG" if stale else "NOTIFICATION_FAILED" if notification_failed else "ALERT_SENT" if changed else "NO_TRIGGER"
    record = {"query_time_bjt": now.isoformat(), "config_date": payload.get("date"), "status": status, "price_source": price_source, "source_failures": source_failures, "prices": prices, "source_quotes": source_quotes, "price_validity": price_validity, "evaluations": evaluations, "notifications": notifications}
    write_audit(audit_path, record)
    print(f"MONITOR_RESULT status={status} audit={audit_path}")
    if notification_failed:
        raise SystemExit("One or more triggered alerts could not be accepted by Feishu")


if __name__ == "__main__":
    main()
