"""Market data providers for realtime polling."""

from __future__ import annotations

from dataclasses import dataclass
import importlib
import importlib.util
from typing import List, Optional

from bot.core.indicators import Candle


@dataclass(frozen=True)
class MarketSnapshot:
    symbol: str
    candles: List[Candle]


class MarketDataError(RuntimeError):
    """Raised when market data cannot be fetched."""


class MarketDataProvider:
    """Base provider."""

    def fetch(self, symbol: str) -> MarketSnapshot:
        raise NotImplementedError


class YFinanceProvider(MarketDataProvider):
    """Fetch OHLCV data using yfinance."""

    def __init__(self, suffix: str) -> None:
        self.suffix = suffix

    def fetch(self, symbol: str) -> MarketSnapshot:
        if importlib.util.find_spec("yfinance") is None:
            raise MarketDataError("yfinance is not installed.")
        yf = importlib.import_module("yfinance")

        ticker = f"{symbol}{self.suffix}"
        data = yf.Ticker(ticker).history(period="7d", interval="1m")
        if data.empty:
            raise MarketDataError(f"No data returned for {ticker}.")
        candles = [
            Candle(
                open=row["Open"],
                high=row["High"],
                low=row["Low"],
                close=row["Close"],
                volume=row["Volume"],
            )
            for _, row in data.iterrows()
        ]
        return MarketSnapshot(symbol=symbol, candles=candles)


class MockProvider(MarketDataProvider):
    """Dummy provider for tests or offline demo."""

    def __init__(self, candles: Optional[List[Candle]] = None) -> None:
        self._candles = candles or [
            Candle(open=100, high=110, low=95, close=105, volume=100000),
            Candle(open=105, high=115, low=100, close=112, volume=120000),
            Candle(open=112, high=120, low=110, close=118, volume=180000),
            Candle(open=118, high=125, low=115, close=121, volume=200000),
        ]

    def fetch(self, symbol: str) -> MarketSnapshot:
        return MarketSnapshot(symbol=symbol, candles=self._candles)
