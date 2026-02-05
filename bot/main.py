"""Entrypoint for the stock bot."""

from __future__ import annotations

import sys
from typing import Callable, Dict

from bot.config import load_settings
from bot.handlers.alert import handle_alert
from bot.handlers.algo import handle_algo
from bot.handlers.screening import handle_scr


CommandHandler = Callable[[], str]


def build_dispatcher() -> Dict[str, CommandHandler]:
    return {
        "/scr": handle_scr,
        "/alert": handle_alert,
        "/algo": handle_algo,
    }


def render_help() -> str:
    return (
        "Stock Bot Dispatcher\n"
        "Perintah tersedia:\n"
        "- /scr   → screening manual\n"
        "- /alert → alarm sekali pakai\n"
        "- /algo  → screening otomatis & berulang\n\n"
        "Contoh:\n"
        "python -m bot.main \"/scr price < 1000 + rsi < 30 title saham murah oversold\""
    )


def run_cli(argv: list[str]) -> int:
    settings = load_settings()
    dispatcher = build_dispatcher()
    if len(argv) < 2:
        print(render_help())
        if not settings.telegram_bot_token:
            print("\n⚠️ TELEGRAM_BOT_TOKEN belum di-set.")
        return 0

    message = " ".join(argv[1:]).strip()
    command = message.split(maxsplit=1)[0]
    handler = dispatcher.get(command)
    if not handler:
        print(render_help())
        return 1

    print(handler())
    return 0


def main() -> None:
    raise SystemExit(run_cli(sys.argv))


if __name__ == "__main__":
    main()
