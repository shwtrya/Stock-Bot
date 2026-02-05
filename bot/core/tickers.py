"""Utilities to load BEI tickers from local files or remote endpoints."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Iterable, List
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class TickerSource:
    file_path: str
    url: str
    url_token: str


def _parse_text_lines(payload: str) -> List[str]:
    tickers = []
    for line in payload.splitlines():
        symbol = line.strip().upper()
        if symbol and not symbol.startswith("#"):
            tickers.append(symbol)
    return tickers


def _parse_json_payload(payload: str) -> List[str]:
    data = json.loads(payload)
    if isinstance(data, dict) and "tickers" in data:
        data = data["tickers"]
    if not isinstance(data, list):
        raise ValueError("JSON payload should be a list of tickers or {tickers:[...]}")
    return [str(item).strip().upper() for item in data if str(item).strip()]


def _parse_csv_payload(payload: str) -> List[str]:
    tickers = []
    for row in payload.splitlines():
        if not row.strip():
            continue
        ticker = row.split(",")[0].strip()
        if ticker.lower() in {"ticker", "symbol"}:
            continue
        tickers.append(ticker.upper())
    return tickers


def _load_from_url(url: str, token: str) -> List[str]:
    headers = {"User-Agent": "Stock-Bot/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, headers=headers)
    with urlopen(request, timeout=20) as response:
        payload = response.read().decode("utf-8")
    if url.endswith(".json"):
        return _parse_json_payload(payload)
    if url.endswith(".csv"):
        return _parse_csv_payload(payload)
    return _parse_text_lines(payload)


def load_tickers(source: TickerSource) -> List[str]:
    if source.url:
        return _load_from_url(source.url, source.url_token)
    if not os.path.exists(source.file_path):
        raise FileNotFoundError(
            f"Ticker file not found: {source.file_path}. "
            "Provide BEI_TICKERS_FILE or BEI_TICKERS_URL."
        )
    with open(source.file_path, "r", encoding="utf-8") as handle:
        return _parse_text_lines(handle.read())


def format_tickers(tickers: Iterable[str]) -> str:
    return ", ".join(sorted(set(tickers)))
