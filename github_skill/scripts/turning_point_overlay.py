from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np

RULE_VERSION = "crypto-turning-point-overlay-shadow-v1"
HORIZONS = {"24h": 6, "72h": 18, "7d": 42}
MIN_HISTORY = 750
MIN_EFFECTIVE_N = 20.0


def _as_rows(klines: Iterable[list[Any]]) -> list[dict[str, float]]:
    rows = []
    for k in klines:
        rows.append({
            "time": float(k[0]), "open": float(k[1]), "high": float(k[2]),
            "low": float(k[3]), "close": float(k[4]), "volume": float(k[5]),
        })
    return rows


def _atr(rows: list[dict[str, float]], period: int = 14) -> np.ndarray:
    out = np.full(len(rows), np.nan)
    tr = np.full(len(rows), np.nan)
    for i, row in enumerate(rows):
        prev = rows[i - 1]["close"] if i else row["close"]
        tr[i] = max(row["high"] - row["low"], abs(row["high"] - prev), abs(row["low"] - prev))
    for i in range(period - 1, len(rows)):
        out[i] = float(np.mean(tr[i - period + 1:i + 1]))
    return out


def _rolling_mean(values: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(values), np.nan)
    for i in range(n - 1, len(values)):
        out[i] = float(np.mean(values[i - n + 1:i + 1]))
    return out


def _rolling_std(values: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(values), np.nan)
    for i in range(n - 1, len(values)):
        out[i] = float(np.std(values[i - n + 1:i + 1], ddof=1))
    return out


def _feature_matrix(rows: list[dict[str, float]]) -> tuple[np.ndarray, list[str]]:
    close = np.array([r["close"] for r in rows], dtype=float)
    volume = np.array([r["volume"] for r in rows], dtype=float)
    logret = np.full(len(rows), np.nan)
    logret[1:] = np.diff(np.log(close))
    ma20, ma60 = _rolling_mean(close, 20), _rolling_mean(close, 60)
    rv20 = _rolling_std(logret, 20) * math.sqrt(6 * 365)
    vol20, volstd20 = _rolling_mean(volume, 20), _rolling_std(volume, 20)
    fields = ["ret_24h", "ret_72h", "ret_7d", "ma20_gap", "ma60_gap", "rv20", "drawdown_7d", "volume_z"]
    x = np.full((len(rows), len(fields)), np.nan)
    for i in range(len(rows)):
        if i >= 6: x[i, 0] = close[i] / close[i - 6] - 1
        if i >= 18: x[i, 1] = close[i] / close[i - 18] - 1
        if i >= 42:
            x[i, 2] = close[i] / close[i - 42] - 1
            x[i, 6] = close[i] / max(close[i - 42:i + 1]) - 1
        if np.isfinite(ma20[i]): x[i, 3] = close[i] / ma20[i] - 1
        if np.isfinite(ma60[i]): x[i, 4] = close[i] / ma60[i] - 1
        x[i, 5] = rv20[i]
        if np.isfinite(volstd20[i]) and volstd20[i] > 0: x[i, 7] = (volume[i] - vol20[i]) / volstd20[i]
    return x, fields


def _label(rows: list[dict[str, float]], atr: np.ndarray, i: int, horizon: int) -> dict[str, Any] | None:
    if not np.isfinite(atr[i]) or i + horizon >= len(rows):
        return None
    ref, unit = rows[i]["close"], atr[i]
    upper, lower = ref + 0.75 * unit, ref - 0.75 * unit
    future = rows[i + 1:i + horizon + 1]
    first_up = next((j for j, r in enumerate(future) if r["high"] >= upper), None)
    first_down = next((j for j, r in enumerate(future) if r["low"] <= lower), None)
    ambiguous = first_up is not None and first_down is not None and first_up == first_down
    low_j = min(range(len(future)), key=lambda j: future[j]["low"])
    high_j = max(range(len(future)), key=lambda j: future[j]["high"])
    low_price, high_price = future[low_j]["low"], future[high_j]["high"]
    bottom = low_price <= lower and any(r["high"] >= low_price + unit for r in future[low_j + 1:])
    top = high_price >= upper and any(r["low"] <= high_price - unit for r in future[high_j + 1:])
    if ambiguous:
        exclusive = "AMBIGUOUS"
    elif first_down is not None and (first_up is None or first_down < first_up) and bottom:
        exclusive = "BOTTOM_REBOUND_FIRST"
    elif first_up is not None and (first_down is None or first_up < first_down) and top:
        exclusive = "TOP_REVERSAL_FIRST"
    else:
        exclusive = "NO_DIRECTIONAL_TURN"
    return {
        "exclusive": exclusive, "bottom_event": bool(bottom), "top_event": bool(top),
        "two_way_wash": bool(bottom and top), "min_price": low_price, "max_price": high_price,
        "terminal": future[-1]["close"], "ref": ref, "atr": unit,
    }


def _weighted_quantile(values: np.ndarray, weights: np.ndarray, qs=(0.25, 0.5, 0.75)) -> list[float]:
    order = np.argsort(values)
    values, weights = values[order], weights[order]
    cdf = np.cumsum(weights) / np.sum(weights)
    return [float(np.interp(q, cdf, values)) for q in qs]


def _envelope(spot: float, annualized_rv: float, horizon_bars: int) -> dict[str, list[float]]:
    move = annualized_rv * math.sqrt(horizon_bars / (6 * 365))
    return {
        "one_sigma": [spot * math.exp(-move), spot * math.exp(move)],
        "two_sigma": [spot * math.exp(-2 * move), spot * math.exp(2 * move)],
    }


def analyze(klines: Iterable[list[Any]], min_history: int = MIN_HISTORY) -> dict[str, Any]:
    rows = _as_rows(klines)
    atr = _atr(rows)
    features, feature_names = _feature_matrix(rows)
    current_i = len(rows) - 1
    result: dict[str, Any] = {
        "rule_version": RULE_VERSION, "resolution": "4h", "completed_bars": len(rows),
        "feature_names": feature_names, "status": "SHADOW_UNCALIBRATED", "horizons": {},
        "note": "历史近邻场景占比（未校准）；不得用于Kelly、仓位或绕过S1-S5。",
    }
    if len(rows) < min_history or not np.all(np.isfinite(features[current_i])):
        result["status"] = "INSUFFICIENT_HISTORY"
    spot = rows[-1]["close"] if rows else None
    for name, horizon in HORIZONS.items():
        sample_idx, labels = [], []
        for i in range(60, max(60, len(rows) - horizon)):
            if np.all(np.isfinite(features[i])):
                label = _label(rows, atr, i, horizon)
                if label is not None:
                    sample_idx.append(i); labels.append(label)
        metric: dict[str, Any] = {"status": result["status"], "mature_n": len(labels)}
        if not labels or spot is None or not np.all(np.isfinite(features[current_i])):
            result["horizons"][name] = metric
            continue
        hist_x = features[sample_idx]
        median = np.nanmedian(hist_x, axis=0)
        scale = np.nanmedian(np.abs(hist_x - median), axis=0) * 1.4826
        scale[~np.isfinite(scale) | (scale < 1e-9)] = 1.0
        distances = np.sqrt(np.mean(((hist_x - features[current_i]) / scale) ** 2, axis=1))
        k = min(max(40, int(math.sqrt(len(labels)) * 4)), 120, len(labels))
        chosen = np.argsort(distances)[:k]
        d = distances[chosen]
        bandwidth = max(float(np.median(d)), 1e-6)
        weights = np.exp(-0.5 * (d / bandwidth) ** 2)
        effective_n = float(weights.sum() ** 2 / np.square(weights).sum())
        selected = [labels[j] for j in chosen]
        eligible = [(lab, w) for lab, w in zip(selected, weights) if lab["exclusive"] != "AMBIGUOUS"]
        denom = sum(w for _, w in eligible)
        shares = {key: (sum(w for lab, w in eligible if lab["exclusive"] == key) / denom if denom else None)
                  for key in ("BOTTOM_REBOUND_FIRST", "TOP_REVERSAL_FIRST", "NO_DIRECTIONAL_TURN")}
        diagnostics = {
            "bottom_event": float(sum(w for lab, w in zip(selected, weights) if lab["bottom_event"]) / weights.sum()),
            "top_event": float(sum(w for lab, w in zip(selected, weights) if lab["top_event"]) / weights.sum()),
            "two_way_wash": float(sum(w for lab, w in zip(selected, weights) if lab["two_way_wash"]) / weights.sum()),
            "ambiguous_share": float(sum(w for lab, w in zip(selected, weights) if lab["exclusive"] == "AMBIGUOUS") / weights.sum()),
        }
        min_rel = np.array([(lab["min_price"] - lab["ref"]) / lab["atr"] for lab in selected])
        max_rel = np.array([(lab["max_price"] - lab["ref"]) / lab["atr"] for lab in selected])
        terminal_rel = np.array([(lab["terminal"] - lab["ref"]) / lab["atr"] for lab in selected])
        unit = atr[current_i]
        low_band = [spot + q * unit for q in _weighted_quantile(min_rel, weights)]
        high_band = [spot + q * unit for q in _weighted_quantile(max_rel, weights)]
        terminal_band = [spot + q * unit for q in _weighted_quantile(terminal_rel, weights, (0.1, 0.5, 0.9))]
        rv = float(features[current_i, feature_names.index("rv20")])
        metric.update({
            "status": "SHADOW_UNCALIBRATED" if len(rows) >= min_history and effective_n >= MIN_EFFECTIVE_N else ("INSUFFICIENT_HISTORY" if len(rows) < min_history else "INSUFFICIENT_EFFECTIVE_N"),
            "neighbor_n": k, "effective_n": effective_n, "scenario_share": shares,
            "diagnostic_share": diagnostics, "conditional_low_band": low_band,
            "conditional_high_band": high_band, "terminal_band": terminal_band,
            "statistical_envelope": _envelope(spot, rv, horizon),
        })
        result["horizons"][name] = metric
    return result


def self_test() -> None:
    rows = []
    price = 100.0
    for i in range(900):
        drift = 0.08 * math.sin(i / 19.0) + 0.03
        close = price + drift
        rows.append([i * 14_400_000, price, max(price, close) + 0.8, min(price, close) - 0.8, close, 1000 + 50 * math.sin(i / 7.0)])
        price = close
    output = analyze(rows)
    assert output["status"] == "SHADOW_UNCALIBRATED"
    for name in HORIZONS:
        metric = output["horizons"][name]
        shares = metric["scenario_share"]
        assert abs(sum(v for v in shares.values() if v is not None) - 1.0) < 1e-9
        assert metric["effective_n"] >= MIN_EFFECTIVE_N
        assert metric["conditional_low_band"][1] <= metric["conditional_high_band"][1]
    print("PASS: crypto turning-point shadow overlay")


if __name__ == "__main__":
    self_test()
