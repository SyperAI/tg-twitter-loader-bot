# Twitter (X) Media Loader Telegram Bot

Telegram bot built with [aiogram 3](https://docs.aiogram.dev/) and [yt-dlp](https://github.com/yt-dlp/yt-dlp) for downloading and sending videos and GIFs from Twitter (X).

> Developed with the assistance of **Antigravity** (Google DeepMind).

## Features

- **Clean & Modular Architecture**: Structured into handlers, services, configuration, and utilities.
- **No Database Needed**: Completely stateless.
- **Supports twitter.com & x.com**: Automatically parses and cleans tracking parameters (`?s=...&t=...`).
- **Video & GIF Support**: GIFs are sent as looping animations (`send_animation`), videos with audio are sent as streaming videos (`send_video`).
- **Local Bot API Server Support**:
  - **Same server mode (`BOT_API_IS_LOCAL=true`)**: Direct local file path access, zero-copy, up to 2000 MB (2 GB).
  - **Remote server mode (`BOT_API_IS_LOCAL=false`)**: Fast HTTP transfer to a remote Local Bot API instance, up to 2000 MB (2 GB).
  - **Cloud mode (default)**: Uses official Telegram Cloud API (up to 50 MB limit).
- **Auto-Cleanup**: Media files are downloaded into isolated temporary directories and deleted immediately after sending.
- **User-Friendly Feedback**: Sends typing/upload action indicators and descriptive English status/error messages.

## Project Structure

```text
twitter-loader-tg-bot/
├── bot/
│   ├── handlers/            # Message and command handlers
│   │   ├── common.py        # /start and /help commands
│   │   └── twitter.py       # Twitter/X link handler and fallback
│   ├── services/            # Background services
│   │   └── downloader.py    # yt-dlp async downloader
│   ├── utils/               # Helpers
│   │   └── link_parser.py   # Regex and URL extraction
│   └── config.py            # Pydantic Settings (.env configuration)
├── main.py                  # Application entry point
├── .env.example             # Configuration template
├── .gitignore               # Ignored files
└── pyproject.toml           # Project dependencies
```

## Quick Start

### 1. Installation
Clone the repository and install dependencies with [uv](https://github.com/astral-sh/uv):
```bash
uv sync
```
Or with standard `pip`:
```bash
pip install -e .
```

### 2. Configuration
Copy the `.env.example` file:
```bash
cp .env.example .env
```

Edit `.env`:

#### Option A: Official Telegram Cloud API (Default)
```env
BOT_TOKEN=your_bot_token_here
```

#### Option B: Local Bot API on the SAME server
```env
BOT_TOKEN=your_bot_token_here
BOT_API_URL=http://localhost:8081
BOT_API_IS_LOCAL=true
```

#### Option C: Local Bot API on a DIFFERENT server / Docker network
```env
BOT_TOKEN=your_bot_token_here
BOT_API_URL=http://192.168.1.100:8081
BOT_API_IS_LOCAL=false
```

### 3. Run the Bot
```bash
# Using uv:
uv run python main.py

# Or directly in your virtual environment:
python main.py
```

## Credits

Developed with the assistance of **Antigravity**, an agentic AI assistant created by the Google DeepMind team.
