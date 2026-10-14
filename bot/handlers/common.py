from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.config import config

router = Router(name="common")


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    """Handles the /start command."""
    text = (
        "👋 **Hello!** I can download videos and GIFs from **Twitter (X)**.\n\n"
        "📎 Simply send me a tweet link containing a video or GIF, "
        "and I will send the media right here!\n\n"
        "ℹ️ More details: /help"
    )
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    """Handles the /help command."""
    limit_mb = config.max_filesize_mb
    text = (
        "📖 **How to use this bot:**\n\n"
        "1. Copy a link to a tweet containing a video or GIF (`twitter.com` or `x.com`).\n"
        "2. Send the link directly in this chat.\n"
        "3. The bot will download and send the media back to you.\n\n"
        "⚠️ **Limitations:**\n"
        "• Private/protected tweets and suspended accounts are not supported.\n"
        f"• Maximum file size limit: {limit_mb} MB."
    )
    await message.answer(text, parse_mode="Markdown")
