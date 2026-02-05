"""Telegram bot implementation with realtime polling."""

from __future__ import annotations

import asyncio
import importlib
import importlib.util
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from bot.config import Settings
from bot.core.engine import run_screening
from bot.core.filters import parse_filters
from bot.core.market_data import MarketDataError, MarketDataProvider, YFinanceProvider
from bot.core.tickers import TickerSource, load_tickers


@dataclass
class AlertState:
    task: asyncio.Task
    active_symbols: Set[str] = field(default_factory=set)


class TelegramBot:
    def __init__(self, settings: Settings, provider: Optional[MarketDataProvider] = None) -> None:
        self.settings = settings
        self.provider = provider or YFinanceProvider(settings.yfinance_suffix)
        self._alerts: Dict[int, AlertState] = {}

    def load_ticker_list(self) -> List[str]:
        source = TickerSource(
            file_path=self.settings.bei_tickers_file,
            url=self.settings.bei_tickers_url,
            url_token=self.settings.bei_tickers_url_token,
        )
        return load_tickers(source)

    async def start(self) -> None:
        if importlib.util.find_spec("telegram") is None:
            raise RuntimeError(
                "python-telegram-bot is required. Install with `pip install python-telegram-bot`."
            )
        telegram_module = importlib.import_module("telegram")
        telegram_ext = importlib.import_module("telegram.ext")
        Update = telegram_module.Update
        Application = telegram_ext.Application
        CommandHandler = telegram_ext.CommandHandler
        ContextTypes = telegram_ext.ContextTypes

        async def scr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            await self._handle_scr(update, context)

        async def alert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            await self._handle_alert(update, context, repeat=False)

        async def algo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            await self._handle_alert(update, context, repeat=True)

        async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            await self._handle_stop(update, context)

        app = Application.builder().token(self.settings.telegram_bot_token).build()
        app.add_handler(CommandHandler("scr", scr))
        app.add_handler(CommandHandler("alert", alert))
        app.add_handler(CommandHandler("algo", algo))
        app.add_handler(CommandHandler("stop", stop))
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        await app.updater.wait()

    async def _handle_scr(self, update, context) -> None:
        message = update.effective_message
        if not message:
            return
        filters_text = " ".join(context.args)
        if not filters_text:
            await message.reply_text("Gunakan: /scr <filter> (contoh: /scr price < 1000 + rsi < 30)")
            return
        await message.reply_text("🔎 Screening berjalan... (realtime untuk semua BEI)")
        await self._run_once(message, filters_text)

    async def _handle_alert(self, update, context, repeat: bool) -> None:
        message = update.effective_message
        if not message:
            return
        filters_text = " ".join(context.args)
        if not filters_text:
            await message.reply_text("Gunakan: /alert <filter> atau /algo <filter>")
            return
        chat_id = message.chat_id
        if chat_id in self._alerts:
            await message.reply_text("Alert sudah aktif. Gunakan /stop untuk menghentikan.")
            return
        await message.reply_text(
            "✅ Realtime monitoring dimulai.\n"
            f"Mode: {'berulang' if repeat else 'sekali tembak'}."
        )
        task = asyncio.create_task(self._alert_loop(chat_id, message, filters_text, repeat))
        self._alerts[chat_id] = AlertState(task=task)

    async def _handle_stop(self, update, context) -> None:
        message = update.effective_message
        if not message:
            return
        chat_id = message.chat_id
        state = self._alerts.pop(chat_id, None)
        if not state:
            await message.reply_text("Tidak ada alert aktif.")
            return
        state.task.cancel()
        await message.reply_text("🛑 Alert dihentikan.")

    async def _alert_loop(self, chat_id: int, message, filters_text: str, repeat: bool) -> None:
        try:
            while True:
                matched = await self._run_once(message, filters_text, track_state=repeat, chat_id=chat_id)
                if matched and not repeat:
                    await message.reply_text("🎯 Alert selesai (sekali tembak).")
                    break
                await asyncio.sleep(self.settings.poll_interval_seconds)
        except asyncio.CancelledError:
            return
        finally:
            self._alerts.pop(chat_id, None)

    async def _run_once(
        self,
        message,
        filters_text: str,
        track_state: bool = False,
        chat_id: Optional[int] = None,
    ) -> bool:
        try:
            conditions = parse_filters(filters_text)
        except ValueError as exc:
            await message.reply_text(f"Format filter salah: {exc}")
            return False

        try:
            tickers = self.load_ticker_list()
        except Exception as exc:  # noqa: BLE001
            await message.reply_text(f"Gagal load ticker BEI: {exc}")
            return False

        results, errors = run_screening(self.provider, tickers, conditions)
        matched = [result.symbol for result in results if result.passed]

        if track_state and chat_id is not None:
            state = self._alerts.get(chat_id)
            if state:
                new_matches = [s for s in matched if s not in state.active_symbols]
                state.active_symbols.update(new_matches)
                matched = new_matches

        if matched:
            await message.reply_text("✅ Saham memenuhi kriteria: " + ", ".join(matched))
        else:
            await message.reply_text("Tidak ada saham yang memenuhi kriteria saat ini.")

        if errors:
            await message.reply_text("⚠️ Beberapa data gagal diambil:\n" + "\n".join(errors[:10]))
        return bool(matched)


def build_bot(settings: Settings) -> TelegramBot:
    return TelegramBot(settings=settings)
