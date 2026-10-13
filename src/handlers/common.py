from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.config import settings
from src.database.models.user import User

common_router = Router(name="common_router")


@common_router.message(Command("help"))
async def help_command_handler(message: Message, db_user: User | None = None) -> None:
    """Handle /help command."""
    is_admin = db_user and db_user.role == "admin"

    help_lines = [
        f"📖 <b>Довідка по командам бота «{settings.SALON_NAME}»:</b>\n",
        "/start — Головне меню студії",
        "/help — Довідка та команди",
    ]

    if is_admin:
        help_lines.append("/admin — Панель керування адміністратора")

    help_lines.append(
        f"\n<i>З будь-яких питань пишіть нашому адміністратору: {settings.ADMIN_USERNAME}</i>"
    )

    await message.answer("\n".join(help_lines))
