"""Configuration loader for the bot."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str


def load_settings() -> Settings:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    return Settings(telegram_bot_token=token)
