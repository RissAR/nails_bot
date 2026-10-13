import asyncio
import logging
import sys
import uvicorn

from aiogram import Bot, Dispatcher
from aiogram.types import MenuButtonWebApp, WebAppInfo

from src.bot import get_bot
from src.api.app import app as fastapi_app
from src.config import settings
from src.database import init_db
from src.handlers import admin_router, client_router, common_router
from src.middlewares import AuthMiddleware
from src.services.reminder_service import run_reminder_worker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


async def run_bot(bot: Bot, dp: Dispatcher) -> None:
    """Run aiogram bot polling and configure menu button."""
    logger.info("Bot starting in polling mode...")
    logger.info("Studio: %s", settings.SALON_NAME)
    logger.info("Configured admins: %s", settings.ADMIN_IDS)
    logger.info("Mini App URL: %s", settings.WEBAPP_URL)

    # Set native chat menu button to WebApp if HTTPS URL is configured
    if settings.WEBAPP_URL.startswith("https://"):
        try:
            webapp_url = settings.get_webapp_url()
            await bot.set_chat_menu_button(
                menu_button=MenuButtonWebApp(
                    text="💅 Запис",
                    web_app=WebAppInfo(url=webapp_url),
                )
            )
            logger.info("Chat menu button set to WebApp: %s", webapp_url)
        except Exception as e:
            logger.warning("Failed to set chat menu button: %s", e)
    else:
        logger.info(
            "WEBAPP_URL is not HTTPS (%s). Telegram requires an HTTPS URL for the native chat menu button. "
            "Configure an HTTPS tunnel (e.g. ngrok) in .env to activate the native menu button.",
            settings.WEBAPP_URL,
        )

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

    bot = get_bot()
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
            run_reminder_worker(bot),
        )
    finally:
        await bot.session.close()
        logger.info("Application shutdown completed.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Application process interrupted.")
