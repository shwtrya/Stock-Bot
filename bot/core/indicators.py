"""Indicator calculations used by filters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Candle:
    open: float
    high: float
    low: float
    close: float
    volume: float


def sma(values: List[float], period: int) -> Optional[float]:
    if len(values) < period or period <= 0:
        return None
    return sum(values[-period:]) / period


def ema(values: List[float], period: int) -> Optional[float]:
    if len(values) < period or period <= 0:
        return None
    multiplier = 2 / (period + 1)
    ema_value = sum(values[:period]) / period
    for value in values[period:]:
        ema_value = (value - ema_value) * multiplier + ema_value
    return ema_value


def rsi(values: List[float], period: int = 14) -> Optional[float]:
    if len(values) < period + 1:
        return None
    gains = []
    losses = []
    for prev, curr in zip(values[-(period + 1) : -1], values[-period:]):
        change = curr - prev
        if change >= 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def roc(values: List[float], period: int = 14) -> Optional[float]:
    if len(values) <= period:
        return None
    prev = values[-(period + 1)]
    if prev == 0:
        return None
    return ((values[-1] - prev) / prev) * 100


def adx(candles: List[Candle], period: int = 14) -> Optional[float]:
    if len(candles) < period + 1:
        return None
    trs = []
    plus_dm = []
    minus_dm = []
    for prev, curr in zip(candles[:-1], candles[1:]):
        tr = max(curr.high - curr.low, abs(curr.high - prev.close), abs(curr.low - prev.close))
        trs.append(tr)
        up_move = curr.high - prev.high
        down_move = prev.low - curr.low
        plus_dm.append(up_move if up_move > down_move and up_move > 0 else 0)
        minus_dm.append(down_move if down_move > up_move and down_move > 0 else 0)
    tr14 = sum(trs[-period:])
    if tr14 == 0:
        return None
    plus_di = 100 * (sum(plus_dm[-period:]) / tr14)
    minus_di = 100 * (sum(minus_dm[-period:]) / tr14)
    dx = 100 * abs(plus_di - minus_di) / max(plus_di + minus_di, 1e-9)
    return dx


def macd(values: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    if len(values) < slow + signal:
        return {"macd": None, "signal": None, "hist": None}
    ema_fast = ema(values, fast)
    ema_slow = ema(values, slow)
    if ema_fast is None or ema_slow is None:
        return {"macd": None, "signal": None, "hist": None}
    macd_line = ema_fast - ema_slow
    history = []
    for i in range(slow, len(values) + 1):
        slice_values = values[:i]
        fast_val = ema(slice_values, fast)
        slow_val = ema(slice_values, slow)
        if fast_val is None or slow_val is None:
            continue
        history.append(fast_val - slow_val)
    signal_val = ema(history, signal) if history else None
    hist = macd_line - signal_val if signal_val is not None else None
    return {"macd": macd_line, "signal": signal_val, "hist": hist}
