"""
Main entry point — Telegram polling + aiohttp health server for Render free tier.
"""

import asyncio
import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db
from logger import setup_logging
from middlewares import LoggingMiddleware

from start import router as start_router
from folder_handler import router as folder_router
from upload_handler import router as upload_router
from json_fetch_handler import router as fetch_router
from stats_handler import router as stats_router

logger = logging.getLogger(__name__)


# ── Health-check web server ───────────────────────────────────────────────────

async def handle_health(request: web.Request) -> web.Response:
    return web.Response(text="OK", status=200)


async def run_web_server() -> None:
    port = int(os.environ.get("PORT", 8080))
    app = web.Application()
    app.router.add_get("/", handle_health)
    app.router.add_get("/health", handle_health)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, host="0.0.0.0", port=port).start()
    logger.info("Health-check server on port %d", port)


# ── Telegram bot ──────────────────────────────────────────────────────────────

async def on_startup(bot: Bot) -> None:
    await init_db()
    me = await bot.get_me()
    logger.info("Bot started: @%s (id=%s)", me.username, me.id)


async def on_shutdown(bot: Bot) -> None:
    logger.info("Bot shutting down...")
    await bot.session.close()


async def run_bot() -> None:
    # No default parse_mode — each handler specifies its own
    bot = Bot(token=BOT_TOKEN)
    dp  = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(LoggingMiddleware())

    dp.include_router(start_router)
    dp.include_router(folder_router)
    dp.include_router(upload_router)
    dp.include_router(fetch_router)
    dp.include_router(stats_router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    logger.info("Starting Telegram polling...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


# ── Entry point ───────────────────────────────────────────────────────────────

async def main() -> None:
    setup_logging()

    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("BOT_TOKEN is not set! Set it in Render Dashboard → Environment Variables.")
        return

    await asyncio.gather(run_web_server(), run_bot())


if __name__ == "__main__":
    asyncio.run(main())
