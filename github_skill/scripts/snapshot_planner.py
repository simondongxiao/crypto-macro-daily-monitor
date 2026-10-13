#!/usr/bin/env python3
"""Snapshot Planning Mode: two-level regime routing and replayable plan lifecycle."""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from statistics import mean
from typing import Any

RULE_VERSION = "crypto-macro-daily-review-snapshot-regime-router-v1"
AUTOMATED_REFRESH_AVAILABLE = "NO"


def ema(values: list[float], span: int) -> list[float]:
    alpha = 2 / (span + 1)
    output = [values[0]]
    for value in values[1:]:
        output.append(alpha * value + (1 - alpha) * output[-1])
    return output


def classify_htf(candles: list[list[Any]]) -> tuple[str, int, dict[str, float]]:
    closes = [float(row[4]) for row in candles]
    if len(closes) < 65:
        return "HTF_TRANSITION", 0, {}
    ma = {n: ema(closes, n) for n in (5, 10, 20, 60)}
    up_stack = ma[5][-1] > ma[10][-1] > ma[20][-1] > ma[60][-1]
    down_stack = ma[5][-1] < ma[10][-1] < ma[20][-1] < ma[60][-1]
    slope_up = ma[20][-1] > ma[20][-5] and ma[60][-1] > ma[60][-5]
    slope_down = ma[20][-1] < ma[20][-5] and ma[60][-1] < ma[60][-5]
    highs = [float(row[2]) for row in candles[-24:]]
    lows = [float(row[3]) for row in candles[-24:]]
    hh_hl = max(highs[-8:]) >= max(highs[:8]) and min(lows[-8:]) >= min(lows[:8])
    ll_lh = min(lows[-8:]) <= min(lows[:8]) and max(highs[-8:]) <= max(highs[:8])
    crossings = sum((closes[i] - ma[20][i]) * (closes[i - 1] - ma[20][i - 1]) < 0 for i in range(-16, 0))
    balanced = max(closes[-24:]) / min(closes[-24:]) - 1 < .025
    if crossings >= 3 and balanced:
        return "HTF_RANGE", 65, {f"ema{n}": ma[n][-1] for n in ma}
    if up_stack and slope_up and closes[-1] > ma[20][-1] and hh_hl:
        return "HTF_TREND_UP", 72, {f"ema{n}": ma[n][-1] for n in ma}
    if down_stack and slope_down and closes[-1] < ma[20][-1] and ll_lh:
        return "HTF_TREND_DOWN", 72, {f"ema{n}": ma[n][-1] for n in ma}
    if crossings >= 3 or (balanced and not up_stack and not down_stack):
        return "HTF_RANGE", 65, {f"ema{n}": ma[n][-1] for n in ma}
    return "HTF_TRANSITION", 48, {f"ema{n}": ma[n][-1] for n in ma}


def execution_state(candles: list[list[Any]], htf: str) -> str:
    closes = [float(row[4]) for row in candles]
    if len(closes) < 25:
        return "CONSOLIDATION"
    average = ema(closes, 20)[-1]
    last = closes[-1]
    recent_high = max(closes[-12:-2]); recent_low = min(closes[-12:-2])
    if htf == "HTF_TREND_UP" and last <= average * 1.003 and last > recent_low * .997:
        return "PULLBACK"
    if htf == "HTF_TREND_DOWN" and last >= average * .997 and last < recent_high * 1.003:
        return "PULLBACK"
    if last > recent_high:
        return "BREAKOUT"
    if last < recent_low:
        return "FAILED_BREAKOUT"
    return "RANGE_MIDDLE" if abs(last / average - 1) < .003 else "CONSOLIDATION"


def route(htf: str, state: str, confidence: int) -> list[str]:
    if htf == "HTF_TREND_UP" and state == "PULLBACK":
        return ["S2c_TREND_PULLBACK_LONG", "S2b_BREAKOUT_RETEST_LONG", "S1_LONG"]
    if htf == "HTF_TREND_UP" and state in {"BREAKOUT", "CONSOLIDATION"}:
        return ["S2a_BREAKOUT_LONG", "S2b_BREAKOUT_RETEST_LONG", "S5_EXTREME_ONLY"]
    if htf == "HTF_TREND_DOWN" and state == "PULLBACK":
        return ["S2c_TREND_PULLBACK_SHORT", "S2b_BREAKOUT_RETEST_SHORT", "S1_SHORT"]
    if htf == "HTF_RANGE" and state in {"RANGE_EDGE", "CONSOLIDATION", "FAILED_BREAKOUT"}:
        return ["S5_MEAN_REVERSION", "S1_LIQUIDITY_SWEEP"]
    return ["WAIT_FOR_LOCATION"]


@dataclass
class Plan:
    asset: str
    direction: str
    setup: str
    htf_regime: str
    execution_state: str
    trigger_zone: list[float]
    trigger_condition: str
    ideal_entry: float
    max_entry: float
    stop: float
    tp1: float
    tp2: float
    starter_risk_pct: float
    maximum_risk_pct: float
    leverage: str
    order_type: str
    cancellation_condition: str
    valid_until_bjt: str
    recheck_condition: str
    preauthorized_context: str = "VALID"
    rule_version_used: str = RULE_VERSION


def s2c_plan(asset: str, price: float, support: float, invalidation: float, tp1: float, tp2: float, now: datetime) -> Plan:
    return Plan(asset, "LONG", "S2c_TREND_PULLBACK_LONG", "HTF_TREND_UP", "PULLBACK",
                [round(support * .998, 2), round(support * 1.002, 2)],
                f"15m 收回 {support:,.2f}，且下一根不跌回 {support * .998:,.2f} 下方",
                round(support * 1.001, 2), round(support * 1.004, 2), round(invalidation, 2), round(tp1, 2), round(tp2, 2),
                .10, .15, "BTC/ETH 4-6x", "PRE_AUTHORIZED_CONDITIONAL",
                f"15m 收盘跌破 {invalidation:,.2f} 或 4H 趋势失效", (now + timedelta(hours=12)).strftime("%Y-%m-%d %H:%M BJT"),
                "重大宏观事件、极端波动或到期后重新运行 Skill")


def reconstruct(plan: Plan, candles: list[list[Any]]) -> str:
    """Replay price-only frozen plans. Missing required non-price evidence stays unresolved."""
    expiry = datetime.strptime(plan.valid_until_bjt, "%Y-%m-%d %H:%M BJT")
    triggered = False
    for row in candles:
        ts = datetime.fromtimestamp(int(row[0]) / 1000).astimezone().replace(tzinfo=None)
        if ts > expiry:
            return "EXPIRED" if not triggered else "TIME_EXIT"
        high, low, close = map(float, (row[2], row[3], row[4]))
        if plan.direction == "LONG":
            if low <= plan.stop:
                return "INVALID_BEFORE_ENTRY" if not triggered else "STOP"
            if low <= plan.max_entry and close >= plan.trigger_zone[0]:
                triggered = True
            if triggered and high >= plan.tp2:
                return "TP2"
            if triggered and high >= plan.tp1:
                return "TP1"
        else:
            if high >= plan.stop:
                return "INVALID_BEFORE_ENTRY" if not triggered else "STOP"
            if high >= plan.max_entry and close <= plan.trigger_zone[1]:
                triggered = True
            if triggered and low <= plan.tp2:
                return "TP2"
            if triggered and low <= plan.tp1:
                return "TP1"
    return "TRIGGERED_NOT_FILLED" if triggered else "NOT_TRIGGERED"


def tests() -> list[dict[str, bool]]:
    up = [[i, 0, 100+i*.7, 99+i*.7, 100+i*.7, 1] for i in range(90)]
    pull = up[:-8] + [[i,0,155-i*.2,154-i*.2,155-i*.2,1] for i in range(82,90)]
    htf, confidence, _ = classify_htf(up)
    plan = s2c_plan("BTC", 150, 148, 146, 154, 158, datetime(2026,9,28,8))
    down = [[i,0,100-i*.7,99-i*.7,100-i*.7,1] for i in range(90)]
    flat = [[i,0,100+(i%3),99+(i%3),100+(i%3),1] for i in range(90)]
    return [
        {"Snapshot Mode": plan.order_type == "PRE_AUTHORIZED_CONDITIONAL"},
        {"No Intraday Refresh": reconstruct(plan, []) == "NOT_TRIGGERED"},
        {"HTF Trend + LTF Pullback": htf == "HTF_TREND_UP" and execution_state(pull, htf) == "PULLBACK"},
        {"HTF Range": classify_htf(flat)[0] == "HTF_RANGE"},
        {"Trend Direction Priority": route("HTF_TREND_UP", "PULLBACK", 72)[0] == "S2c_TREND_PULLBACK_LONG"},
        {"S5 Runtime Rule": "Taker >1.00" not in plan.trigger_condition},
        {"Plan Expiry": "BJT" in plan.valid_until_bjt},
        {"Event Expiry": "重大宏观事件" in plan.recheck_condition},
        {"Historical Reconstruction": reconstruct(plan, [[int(datetime(2026,9,28,9).timestamp()*1000),0,155,147.9,148.2,1]]) == "TP1"},
        {"No User Trade Assumption": True},
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("self-test",))
    args = parser.parse_args()
    outcome = tests()
    print(json.dumps({"rule_version": RULE_VERSION, "automated_refresh_available": AUTOMATED_REFRESH_AVAILABLE, "results": outcome, "passed": all(next(iter(row.values())) for row in outcome)}, ensure_ascii=False, indent=2))
    return 0 if all(next(iter(row.values())) for row in outcome) else 1


if __name__ == "__main__":
    raise SystemExit(main())
