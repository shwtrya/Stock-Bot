"""Configuration loader for the bot."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    bei_tickers_file: str
    bei_tickers_url: str
    bei_tickers_url_token: str
    poll_interval_seconds: int
    yfinance_suffix: str


def load_settings() -> Settings:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    tickers_file = os.getenv("BEI_TICKERS_FILE", "data/bei_tickers.txt")
    tickers_url = os.getenv("BEI_TICKERS_URL", "")
    tickers_url_token = os.getenv("BEI_TICKERS_URL_TOKEN", "")
    poll_interval = int(os.getenv("POLL_INTERVAL_SECONDS", "15"))
    yfinance_suffix = os.getenv("YFINANCE_SUFFIX", ".JK")
    return Settings(
        telegram_bot_token=token,
        bei_tickers_file=tickers_file,
        bei_tickers_url=tickers_url,
        bei_tickers_url_token=tickers_url_token,
        poll_interval_seconds=poll_interval,
        yfinance_suffix=yfinance_suffix,
    )
