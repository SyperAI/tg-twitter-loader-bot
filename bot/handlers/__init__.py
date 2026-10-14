from aiogram import Router

from bot.handlers.common import router as common_router
from bot.handlers.twitter import router as twitter_router


def setup_routers() -> Router:
    """Combines and registers all routers in appropriate order."""
    main_router = Router(name="main_router")
    main_router.include_router(common_router)
    main_router.include_router(twitter_router)
    return main_router
