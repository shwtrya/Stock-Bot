"""Filter parsing utilities."""

from dataclasses import dataclass
from typing import Callable, List, Optional
import re

from bot.core.indicators import Candle, adx, ema, macd, roc, rsi, sma
from bot.core.market_data import MarketSnapshot

@dataclass(frozen=True)
class FilterCondition:
    field: str
    operator: str
    value: str


_FILTER_PATTERN = re.compile(
    r"^(?P<field>[a-zA-Z0-9_]+)\s*(?P<op><=|>=|==|=|<|>)\s*(?P<value>.+)$"
)


def parse_filter_expression(expression: str) -> FilterCondition:
    match = _FILTER_PATTERN.match(expression.strip())
    if not match:
        raise ValueError(f"Invalid filter expression: {expression}")
    return FilterCondition(
        field=match.group("field"),
        operator=match.group("op"),
        value=match.group("value").strip(),
    )


def parse_filters(text: str) -> List[FilterCondition]:
    if not text.strip():
        return []
    expressions = [chunk.strip() for chunk in text.split("+") if chunk.strip()]
    return [parse_filter_expression(expr) for expr in expressions]


def _resolve_period(field: str, prefix: str, default: int) -> int:
    if field.startswith(prefix):
        suffix = field[len(prefix) :]
        if suffix.isdigit():
            return int(suffix)
    return default


def _extract_prev(field: str) -> tuple[int, str]:
    match = re.match(r"^prev(?P<period>\\d+)(?P<name>[a-zA-Z0-9_]+)$", field)
    if not match:
        return 0, field
    return int(match.group("period")), match.group("name")


def _candle_from_snapshot(snapshot: MarketSnapshot) -> Candle:
    if not snapshot.candles:
        raise ValueError("No candle data available.")
    return snapshot.candles[-1]


def _value_for_field(field: str, snapshot: MarketSnapshot) -> Optional[float]:
    candles = snapshot.candles
    if not candles:
        return None
    offset, base_field = _extract_prev(field)
    if offset >= len(candles):
        return None
    candle = candles[-1 - offset]
    if base_field in {"open", "high", "low", "close", "price"}:
        return float(getattr(candle, "close" if base_field == "price" else base_field))
    if base_field == "volume" or base_field == "vol":
        return float(candle.volume)
    if base_field == "gain":
        if len(candles) < 2 + offset:
            return None
        prev_close = candles[-2 - offset].close
        if prev_close == 0:
            return None
        return ((candle.close - prev_close) / prev_close) * 100

    close_values = [c.close for c in candles[: len(candles) - offset]]
    volume_values = [c.volume for c in candles[: len(candles) - offset]]

    if base_field.startswith("ma") and base_field.endswith("vol"):
        period = _resolve_period(base_field, "ma", 20)
        return sma(volume_values, period)
    if base_field.startswith("ma"):
        period = _resolve_period(base_field, "ma", 20)
        return sma(close_values, period)
    if base_field.startswith("ema"):
        period = _resolve_period(base_field, "ema", 20)
        return ema(close_values, period)
    if base_field.startswith("rsi"):
        period = _resolve_period(base_field, "rsi", 14)
        return rsi(close_values, period)
    if base_field.startswith("roc"):
        period = _resolve_period(base_field, "roc", 14)
        return roc(close_values, period)
    if base_field == "adx":
        return adx(candles)
    if base_field in {"macd", "macds", "macdl", "macdh"}:
        values = macd(close_values)
        mapping = {"macd": "macd", "macdl": "macd", "macds": "signal", "macdh": "hist"}
        return values[mapping[base_field]]
    return None


def _parse_value(value: str) -> float:
    return float(value.replace(",", ""))


_OPERATORS: dict[str, Callable[[float, float], bool]] = {
    "<": lambda left, right: left < right,
    "<=": lambda left, right: left <= right,
    ">": lambda left, right: left > right,
    ">=": lambda left, right: left >= right,
    "=": lambda left, right: left == right,
    "==": lambda left, right: left == right,
}


def evaluate_filters(conditions: List[FilterCondition], snapshot: MarketSnapshot) -> bool:
    for condition in conditions:
        left = _value_for_field(condition.field.lower(), snapshot)
        if left is None:
            return False
        right = _parse_value(condition.value)
        operator = _OPERATORS.get(condition.operator)
        if operator is None:
            return False
        if not operator(left, right):
            return False
    return True
