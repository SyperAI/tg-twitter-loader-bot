from pathlib import Path
from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    bot_token: SecretStr = SecretStr("")

    # Local Telegram Bot API configuration (optional)
    # Example: "http://localhost:8081" or "http://192.168.1.100:8081"
    bot_api_url: str | None = None

    # Set to True if the Local Bot API server is running on the SAME machine/filesystem
    # as this bot. When True, aiogram passes file paths directly without HTTP multipart overhead.
    # Set to False if Local Bot API runs on a DIFFERENT server/container.
    bot_api_is_local: bool = False

    # Maximum file size allowed for upload in megabytes.
    # If not explicitly specified:
    # - 2000 MB when using a Local Bot API server
    # - 50 MB when using standard Telegram Cloud Bot API
    custom_max_filesize_mb: int | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def max_filesize_mb(self) -> int:
        if self.custom_max_filesize_mb is not None:
            return self.custom_max_filesize_mb
        return 2000 if self.bot_api_url else 50

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


config = Settings()
