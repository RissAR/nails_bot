from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_admin_main_kb() -> InlineKeyboardMarkup:
    """Return main admin control panel inline keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📋 Список послуг",
                    callback_data="admin_services",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📅 Графік майстрів",
                    callback_data="admin_masters_schedule",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔔 Активні заявки",
                    callback_data="admin_pending_appointments",
                )
            ],
        ]
    )


def get_admin_back_kb() -> InlineKeyboardMarkup:
    """Return back button to admin panel."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="◀️ Назад в адмін-панель",
                    callback_data="admin_main_menu",
                )
            ]
        ]
    )
