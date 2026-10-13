from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_client_main_kb() -> InlineKeyboardMarkup:
    """Return main client inline keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💅 Онлайн-запис (Скоро)",
                    callback_data="client_booking_soon",
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ Про салон",
                    callback_data="client_about",
                ),
                InlineKeyboardButton(
                    text="📞 Контакти",
                    callback_data="client_contacts",
                ),
            ],
        ]
    )


def get_client_back_kb() -> InlineKeyboardMarkup:
    """Return back button to client main menu."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="◀️ Назад до меню",
                    callback_data="client_main_menu",
                )
            ]
        ]
    )
