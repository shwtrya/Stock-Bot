"""Screening engine that evaluates filters over a list of tickers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

from bot.core.filters import evaluate_filters
from bot.core.market_data import MarketDataProvider, MarketSnapshot


@dataclass(frozen=True)
class ScreeningResult:
    symbol: str
    passed: bool
    snapshot: MarketSnapshot


def run_screening(
    provider: MarketDataProvider,
    tickers: Iterable[str],
    conditions: list,
) -> Tuple[List[ScreeningResult], List[str]]:
    results: List[ScreeningResult] = []
    errors: List[str] = []
    for symbol in tickers:
        try:
            snapshot = provider.fetch(symbol)
            passed = evaluate_filters(conditions, snapshot)
            results.append(ScreeningResult(symbol=symbol, passed=passed, snapshot=snapshot))
        except Exception as exc:  # noqa: BLE001 - keep engine resilient
            errors.append(f"{symbol}: {exc}")
    return results, errors
