#!/usr/bin/env python3
"""Poll Binance spot prices and send one Feishu alert per active condition side."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import requests

BINANCE_URL = "https://api.binance.com/api/v3/ticker/price"
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


def fetch_prices(session: requests.Session) -> dict[str, float]:
    response = session.get(
        BINANCE_URL,
        params={"symbols": json.dumps(list(SYMBOLS), separators=(",", ":"))},
        timeout=15,
    )
    response.raise_for_status()
    rows = response.json()
    prices = {row["symbol"]: float(row["price"]) for row in rows}
    missing = [symbol for symbol in SYMBOLS if symbol not in prices]
    if missing:
        raise RuntimeError(f"Binance response missing: {', '.join(missing)}")
    return prices


def signal_text(side: str) -> str:
    if side == "long":
        return "进入多头观察区后，15m/30m 先确认扫低收回、形成 HL，且 Taker/CVD 不再恶化；提醒不等于直接下单。"
    return "进入空头观察区后，15m/30m 先确认冲高失败、跌回关键区下方、形成 LH，且 Taker/CVD 没有重新转强；提醒不等于直接下单。"


def send_feishu(session: requests.Session, webhook: str, symbol: str, side: str, price: float, zone: list[float]) -> None:
    direction = "做多观察区" if side == "long" else "做空观察区"
    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "template": "green" if side == "long" else "red",
            "title": {"tag": "plain_text", "content": f"Crypto 条件区触发：{ASSET_NAMES[symbol]} {direction}"},
        },
        "elements": [
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**品种：** {ASSET_NAMES[symbol]} (`{symbol}`)\n**实时价格：** `{price:,.8f}`\n**触发区间：** `{zone[0]:,.8f} - {zone[1]:,.8f}`"}},
            {"tag": "hr"},
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**微观确认：** {signal_text(side)}"}},
            {"tag": "note", "elements": [{"tag": "plain_text", "content": "来源：Binance public spot ticker；请以 Daily Review 的 SL、TP、Max Entry 和失效条件为准。"}]},
        ],
    }
    response = session.post(webhook, json={"msg_type": "interactive", "card": card}, timeout=15)
    response.raise_for_status()
    body = response.json()
    if body.get("code", 0) not in (0, None):
        raise RuntimeError(f"Feishu rejected card: {body}")


def atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=os.environ.get("ACTIVE_CONDITIONS_PATH", "config/active_conditions.json"))
    parser.add_argument("--webhook", default=os.environ.get("FEISHU_WEBHOOK_URL"))
    parser.add_argument("--dry-run", action="store_true", help="fetch and evaluate prices without sending or writing alerts")
    args = parser.parse_args()

    config_path = Path(args.config)
    payload = load_conditions(config_path)
    session = requests.Session()
    session.headers["User-Agent"] = "crypto-macro-daily-review-price-monitor/1.0"
    prices = fetch_prices(session)
    print(json.dumps({"date": payload.get("date"), "prices": prices}, ensure_ascii=False))

    changed = False
    for symbol in SYMBOLS:
        item = payload["assets"][symbol]
        for side in ("long", "short"):
            zone = item[f"{side}_zone"]
            flag = f"alerted_{side}"
            if not zone or item[flag] or not (zone[0] <= prices[symbol] <= zone[1]):
                continue
            if args.dry_run:
                print(f"DRY_RUN trigger {symbol} {side} {prices[symbol]} in {zone}")
                continue
            if not args.webhook:
                raise SystemExit("FEISHU_WEBHOOK_URL is required when an alert is triggered")
            send_feishu(session, args.webhook, symbol, side, prices[symbol], zone)
            item[flag] = True
            changed = True
            print(f"alerted {symbol} {side} at {prices[symbol]}")

    if changed and not args.dry_run:
        atomic_write(config_path, payload)
        print(f"updated {config_path}")
    else:
        print("no alert state change")


if __name__ == "__main__":
    main()
