import asyncio
import logging
import sys
import uvicorn

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.api.app import app as fastapi_app
from src.config import settings
from src.database import init_db
from src.handlers import admin_router, client_router, common_router
from src.middlewares import AuthMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


async def run_bot(bot: Bot, dp: Dispatcher) -> None:
    """Run aiogram bot polling."""
    logger.info("Bot starting in polling mode...")
    logger.info("Studio: %s", settings.SALON_NAME)
    logger.info("Configured admins: %s", settings.ADMIN_IDS)
    logger.info("Mini App URL: %s", settings.WEBAPP_URL)

    # Drop pending updates to avoid old messages on start
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def run_api() -> None:
    """Run uvicorn FastAPI server."""
    logger.info("Starting FastAPI server on %s:%d...", settings.API_HOST, settings.API_PORT)
    config = uvicorn.Config(
        app=fastapi_app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level="info",
    )
    server = uvicorn.Server(config)
    await server.serve()


async def main() -> None:
    """Main application entry point."""
    logger.info("Initializing database for %s...", settings.SALON_NAME)
    await init_db()
    logger.info("Database initialized successfully.")

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Register Middlewares
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())

    # Register Routers (admin first to intercept admin /start)
    dp.include_router(admin_router)
    dp.include_router(client_router)
    dp.include_router(common_router)

    try:
        await asyncio.gather(
            run_api(),
            run_bot(bot, dp),
        )
    finally:
        await bot.session.close()
        logger.info("Application shutdown completed.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Application process interrupted.")
