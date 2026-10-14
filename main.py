import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode

from bot.config import config
from bot.handlers import setup_routers


async def main() -> None:
    """Entry point for the Telegram bot."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
    logger = logging.getLogger("bot")

    bot_token = config.bot_token.get_secret_value().strip()
    if not bot_token:
        logger.error(
            "BOT_TOKEN is not configured! Please create a .env file based on .env.example and set your BOT_TOKEN."
        )
        sys.exit(1)

    logger.info("Starting Twitter Loader bot...")

    # Configure session for custom/local Bot API server if specified
    session: AiohttpSession | None = None
    if config.bot_api_url:
        api_server = TelegramAPIServer.from_base(
            config.bot_api_url,
            is_local=config.bot_api_is_local,
        )
        session = AiohttpSession(api=api_server)
        logger.info(
            "Configured Local Bot API server: %s (is_local=%s, max upload limit=%d MB)",
            config.bot_api_url,
            config.bot_api_is_local,
            config.max_filesize_mb,
        )
    else:
        logger.info(
            "Using official Telegram Cloud Bot API (max upload limit=%d MB)",
            config.max_filesize_mb,
        )

    bot = Bot(
        token=bot_token,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Register handlers
    dp.include_router(setup_routers())

    # Skip any pending updates to avoid processing outdated messages on launch
    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("Bot is ready and listening for updates.")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
