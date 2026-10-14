import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
import logging
from pathlib import Path
import tempfile
from typing import AsyncIterator

import yt_dlp
from yt_dlp.utils import DownloadError

logger = logging.getLogger(__name__)


@dataclass
class MediaItem:
    """Represents a downloaded video or gif item ready to be sent."""

    file_path: Path
    title: str | None = None
    width: int | None = None
    height: int | None = None
    duration: int | None = None
    is_gif: bool = False
    filesize: int = 0


class TwitterDownloadError(Exception):
    """Base exception for Twitter download issues."""


class NoMediaFoundError(TwitterDownloadError):
    """Raised when the tweet has no video or gif content."""


class FileTooLargeError(TwitterDownloadError):
    """Raised when the downloaded media exceeds the Telegram upload limit."""


class TwitterDownloader:
    """Service for extracting and downloading media from Twitter / X."""

    def __init__(self, max_filesize_mb: int = 50) -> None:
        self.max_filesize_mb = max_filesize_mb
        self.max_filesize_bytes = max_filesize_mb * 1024 * 1024

    @asynccontextmanager
    async def download(self, url: str) -> AsyncIterator[list[MediaItem]]:
        """
        Asynchronously downloads media from a Twitter / X URL.
        Yields a list of MediaItem objects within a temporary directory context.
        Files are automatically deleted when the context block exits.
        """
        loop = asyncio.get_running_loop()

        with tempfile.TemporaryDirectory(prefix="tw_dl_") as tmp_dir:
            temp_path = Path(tmp_dir)
            media_items = await loop.run_in_executor(
                None, self._sync_download, url, temp_path
            )
            yield media_items

    def _sync_download(self, url: str, output_dir: Path) -> list[MediaItem]:
        """Synchronous worker function that executes yt-dlp."""
        outtmpl = str(output_dir / "%(id)s_%(playlist_index)s.%(ext)s")

        ydl_opts = {
            "outtmpl": outtmpl,
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "merge_output_format": "mp4",
            "noplaylist": False,
            "quiet": True,
            "no_warnings": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
        except DownloadError as exc:
            err_msg = str(exc).lower()
            logger.warning("yt-dlp download error for %s: %s", url, exc)
            if "no video" in err_msg or "no media" in err_msg:
                raise NoMediaFoundError(
                    "No video or GIF found in this tweet."
                ) from exc
            if any(term in err_msg for term in ("not found", "404", "does not exist")):
                raise TwitterDownloadError(
                    "Tweet not found or has been deleted."
                ) from exc
            if any(term in err_msg for term in ("protected", "private", "suspended", "not authorized")):
                raise TwitterDownloadError(
                    "This tweet is protected or the account is private/suspended."
                ) from exc
            raise TwitterDownloadError(
                "Failed to download media from tweet. Please try again later."
            ) from exc
        except Exception as exc:
            logger.exception("Unexpected error while downloading %s: %s", url, exc)
            raise TwitterDownloadError(
                "An unexpected error occurred while downloading media."
            ) from exc

        if not info:
            raise NoMediaFoundError("No video or GIF found in this tweet.")

        raw_entries = info.get("entries")
        entries = raw_entries if raw_entries is not None else [info]

        # Gather downloaded files in the output directory
        downloaded_files = sorted(
            [f for f in output_dir.iterdir() if f.is_file() and not f.name.endswith(".part")]
        )

        if not downloaded_files:
            raise NoMediaFoundError("No media files found in this tweet.")

        media_items: list[MediaItem] = []

        for idx, file_path in enumerate(downloaded_files):
            file_size = file_path.stat().st_size
            if file_size > self.max_filesize_bytes:
                size_mb = file_size / (1024 * 1024)
                raise FileTooLargeError(
                    f"Video file ({size_mb:.1f} MB) exceeds the upload limit ({self.max_filesize_mb} MB)."
                )

            # Match metadata with corresponding entry if available
            entry = entries[idx] if idx < len(entries) else entries[0]

            duration = entry.get("duration")
            if duration is not None:
                duration = int(duration)

            width = entry.get("width")
            height = entry.get("height")
            title = entry.get("title") or entry.get("description")
            if title and len(title) > 200:
                title = title[:197] + "..."

            acodec = entry.get("acodec")
            # Twitter GIFs have no audio stream and are usually short
            is_gif = (acodec == "none" or not acodec) and (duration is None or duration <= 60)

            media_items.append(
                MediaItem(
                    file_path=file_path,
                    title=title,
                    width=int(width) if width else None,
                    height=int(height) if height else None,
                    duration=duration,
                    is_gif=is_gif,
                    filesize=file_size,
                )
            )

        return media_items
