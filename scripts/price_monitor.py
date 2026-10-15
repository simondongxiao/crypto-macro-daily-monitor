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
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
ASSET_NAMES = {"BTCUSDT": "BTC", "ETHUSDT": "ETH", "SOLUSDT": "SOL"}


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
    return payload


def fetch_prices(session: requests.Session) -> tuple[dict[str, float], str, list[str]]:
    failures: list[str] = []
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
                return prices, endpoint, failures
            failures.append(f"{endpoint}: missing {','.join(missing)}")
        except (requests.RequestException, KeyError, TypeError, ValueError, RuntimeError) as error:
            failures.append(f"{endpoint}: {error}")

    try:
        response = session.get(COINGECKO_URL, params={"ids": "bitcoin,ethereum,solana", "vs_currencies": "usd"}, timeout=15)
        response.raise_for_status()
        rows = response.json()
        prices = {
            "BTCUSDT": float(rows["bitcoin"]["usd"]),
            "ETHUSDT": float(rows["ethereum"]["usd"]),
            "SOLUSDT": float(rows["solana"]["usd"]),
        }
        return prices, COINGECKO_URL, failures
    except (requests.RequestException, KeyError, TypeError, ValueError) as error:
        raise RuntimeError(f"Binance and CoinGecko public endpoints failed: {failures}; {error}") from error


def signal_text(side: str) -> str:
    if side == "long":
        return "进入多头观察区后，15m/30m 先确认扫低收回、形成 HL，且 Taker/CVD 不再恶化；提醒不等于直接下单。"
    return "进入空头观察区后，15m/30m 先确认冲高失败、跌回关键区下方、形成 LH，且 Taker/CVD 没有重新转强；提醒不等于直接下单。"


def send_feishu(session: requests.Session, webhook: str, symbol: str, side: str, price: float, zone: list[float]) -> dict[str, Any]:
    direction = "做多观察区" if side == "long" else "做空观察区"
    card = {
        "config": {"wide_screen_mode": True},
        "header": {"template": "green" if side == "long" else "red", "title": {"tag": "plain_text", "content": f"Crypto 条件区触发：{ASSET_NAMES[symbol]} {direction}"}},
        "elements": [
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**品种：** {ASSET_NAMES[symbol]} (`{symbol}`)\n**实时价格：** `{price:,.8f}`\n**触发区间：** `{zone[0]:,.8f} - {zone[1]:,.8f}`"}},
            {"tag": "hr"},
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**微观确认：** {signal_text(side)}"}},
            {"tag": "note", "elements": [{"tag": "plain_text", "content": "来源：Binance public ticker；若 GitHub runner 受地区限制则使用 CoinGecko 公共报价兜底。请以 Daily Review 的 SL、TP、Max Entry 和失效条件为准。"}]},
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
    prices, price_source, source_failures = fetch_prices(session)
    today = now.date().isoformat()
    evaluations: list[dict[str, Any]] = []
    notifications: list[dict[str, Any]] = []
    stale = payload.get("date") != today
    notification_failed = False

    print(f"MONITOR_RUN query_time_bjt={now.isoformat()} config_date={payload.get('date')} today={today}")
    print(f"PRICE_SOURCE source={price_source}")
    print(f"PRICE BTC={prices['BTCUSDT']} ETH={prices['ETHUSDT']} SOL={prices['SOLUSDT']}")
    if source_failures:
        print(f"PRICE_SOURCE_FALLBACK failures={source_failures}")

    changed = False
    for symbol in SYMBOLS:
        item = payload["assets"][symbol]
        print(f"ZONE {symbol} long={item['long_zone']} short={item['short_zone']} alerted_long={item['alerted_long']} alerted_short={item['alerted_short']}")
        for side in ("long", "short"):
            zone = item[f"{side}_zone"]
            flag = f"alerted_{side}"
            if stale:
                reason = "STALE_CONFIG_DATE"
            elif not zone:
                reason = "NO_ZONE"
            elif item[flag]:
                reason = "ALREADY_ALERTED"
            elif not (zone[0] <= prices[symbol] <= zone[1]):
                reason = "OUTSIDE_ZONE"
            else:
                reason = "TRIGGERED"
            evaluation = {"symbol": symbol, "side": side, "price": prices[symbol], "zone": zone, "reason": reason}
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
                body = send_feishu(session, args.webhook, symbol, side, prices[symbol], zone)
                item[flag] = True
                atomic_write(config_path, payload)
                changed = True
                notifications.append({"symbol": symbol, "side": side, "status": "SENT_AND_ACCEPTED", "feishu_code": body.get("code")})
                print(f"NOTIFICATION_SENT {symbol} {side} price={prices[symbol]} feishu_code={body.get('code')}")
            except Exception as error:
                notifications.append({"symbol": symbol, "side": side, "status": "NOTIFICATION_FAILED", "reason": str(error)[:300]})
                print(f"NOTIFICATION_FAILED {symbol} {side} reason={error}")
                notification_failed = True

    status = "STALE_CONFIG" if stale else "NOTIFICATION_FAILED" if notification_failed else "ALERT_SENT" if changed else "NO_TRIGGER"
    record = {"query_time_bjt": now.isoformat(), "config_date": payload.get("date"), "status": status, "price_source": price_source, "source_failures": source_failures, "prices": prices, "evaluations": evaluations, "notifications": notifications}
    write_audit(audit_path, record)
    print(f"MONITOR_RESULT status={status} audit={audit_path}")
    if notification_failed:
        raise SystemExit("One or more triggered alerts could not be accepted by Feishu")


if __name__ == "__main__":
    main()
