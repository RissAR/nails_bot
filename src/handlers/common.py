from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.database.models.user import User

common_router = Router(name="common_router")


@common_router.message(Command("help"))
async def help_command_handler(message: Message, db_user: User | None = None) -> None:
    """Handle /help command."""
    is_admin = db_user and db_user.role == "admin"

    help_lines = [
        "📖 <b>Довідка по командам бота:</b>\n",
        "/start — Головне меню",
        "/help — Інформація про команди",
    ]

    if is_admin:
        help_lines.append("/admin — Панель керування адміністратора")

    help_lines.append(
        "\n<i>Якщо у вас виникли запитання, зв'яжіться з нашим адміністратором.</i>"
    )

    await message.answer("\n".join(help_lines))
