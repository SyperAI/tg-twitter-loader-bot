import logging

from aiogram import Bot, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Filter
from aiogram.types import FSInputFile, Message
from aiogram.utils.chat_action import ChatActionSender

from bot.config import config
from bot.services.downloader import (
    FileTooLargeError,
    NoMediaFoundError,
    TwitterDownloader,
    TwitterDownloadError,
)
from bot.utils.link_parser import extract_twitter_urls

logger = logging.getLogger(__name__)

router = Router(name="twitter")
downloader = TwitterDownloader(max_filesize_mb=config.max_filesize_mb)


class TwitterLinkFilter(Filter):
    """Filter that matches messages containing Twitter/X links and injects them."""

    async def __call__(self, message: Message) -> bool | dict[str, list[str]]:
        if not message.text:
            return False
        urls = extract_twitter_urls(message.text)
        if not urls:
            return False
        return {"twitter_urls": urls}


@router.message(TwitterLinkFilter())
async def handle_twitter_links(
    message: Message, twitter_urls: list[str], bot: Bot
) -> None:
    """Processes Twitter links found in user message."""
    for url in twitter_urls:
        status_msg = await message.reply("⏳ Downloading media from Twitter (X)...")

        try:
            async with ChatActionSender.upload_video(chat_id=message.chat.id, bot=bot):
                async with downloader.download(url) as media_items:
                    for item in media_items:
                        file_input = FSInputFile(
                            path=item.file_path, filename=item.file_path.name
                        )

                        if item.is_gif:
                            try:
                                await message.reply_animation(
                                    animation=file_input,
                                    caption=item.title,
                                )
                                continue
                            except Exception as anim_err:
                                logger.warning(
                                    "Failed to send as animation, falling back to video: %s",
                                    anim_err,
                                )

                        await message.reply_video(
                            video=file_input,
                            caption=item.title,
                            width=item.width,
                            height=item.height,
                            duration=item.duration,
                            supports_streaming=True,
                        )

            # Cleanup status message once sent
            try:
                await status_msg.delete()
            except TelegramBadRequest:
                pass

        except NoMediaFoundError as exc:
            await status_msg.edit_text(f"⚠️ {exc}")
        except FileTooLargeError as exc:
            await status_msg.edit_text(f"⚠️ {exc}")
        except TwitterDownloadError as exc:
            await status_msg.edit_text(f"❌ {exc}")
        except Exception as exc:
            logger.exception("Unexpected error processing %s: %s", url, exc)
            await status_msg.edit_text(
                "❌ An unexpected error occurred while processing the video."
            )


@router.message()
async def handle_unknown_message(message: Message) -> None:
    """Fallback handler for non-Twitter messages."""
    await message.reply(
        "ℹ️ Please send a link to a tweet with a video or GIF "
        "(e.g., `https://x.com/...` or `https://twitter.com/...`)."
    )
