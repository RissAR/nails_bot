from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from src.config import settings


def get_admin_main_kb() -> InlineKeyboardMarkup:
    """Return main admin control panel inline keyboard with WebApp."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📱 Відкрити адмін-панель TMA",
                    web_app=WebAppInfo(url=f"{settings.WEBAPP_URL}?role=admin"),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📋 Список послуг",
                    callback_data="admin_services",
                ),
                InlineKeyboardButton(
                    text="👩‍🎨 Майстри та розклад",
                    callback_data="admin_masters_schedule",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔔 Активні заявки",
                    callback_data="admin_pending_appointments",
                ),
                InlineKeyboardButton(
                    text="📊 Клієнти студії",
                    callback_data="admin_clients_stats",
                ),
            ],
        ]
    )


def get_admin_back_kb() -> InlineKeyboardMarkup:
    """Return back button to admin panel with quick TMA link."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📱 Відкрити адмін-панель TMA",
                    web_app=WebAppInfo(url=f"{settings.WEBAPP_URL}?role=admin"),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="◀️ Назад в адмін-панель",
                    callback_data="admin_main_menu",
                ),
            ],
        ]
    )
