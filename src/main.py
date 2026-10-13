import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.config import settings
from src.database.session import init_db
from src.handlers import admin_router, client_router, common_router
from src.middlewares import AuthMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Main bot entry point."""
    logger.info("Initializing database...")
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

    logger.info("Bot starting in polling mode...")
    logger.info("Configured admins: %s", settings.ADMIN_IDS)

    try:
        # Drop pending updates to avoid old messages on start
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot process interrupted.")
