from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from src.config import settings
from src.database.models.category import Category


def get_client_main_kb() -> InlineKeyboardMarkup:
    """Return main client interactive inline keyboard with WebApp button."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💅 Онлайн-запис (Mini App)",
                    web_app=WebAppInfo(url=settings.WEBAPP_URL),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="💅 Послуги та ціни",
                    callback_data="client_services",
                ),
                InlineKeyboardButton(
                    text="👩‍🎨 Наші майстри",
                    callback_data="client_masters",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📍 Контакти",
                    callback_data="client_contacts",
                ),
            ],
        ]
    )


def get_categories_kb(categories: list[Category]) -> InlineKeyboardMarkup:
    """Return keyboard with categories from database."""
    buttons = [
        [
            InlineKeyboardButton(
                text=f"✨ {cat.name}",
                callback_data=f"client_cat:{cat.id}",
            )
        ]
        for cat in categories
    ]
    buttons.append(
        [
            InlineKeyboardButton(
                text="💅 Записатися в Mini App",
                web_app=WebAppInfo(url=settings.WEBAPP_URL),
            )
        ]
    )
    buttons.append(
        [
            InlineKeyboardButton(
                text="◀️ Назад до меню",
                callback_data="client_main_menu",
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_category_services_kb() -> InlineKeyboardMarkup:
    """Return keyboard with navigation back to categories."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💅 Записатися в Mini App",
                    web_app=WebAppInfo(url=settings.WEBAPP_URL),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="◀️ До категорій",
                    callback_data="client_services",
                ),
                InlineKeyboardButton(
                    text="🏠 Головне меню",
                    callback_data="client_main_menu",
                ),
            ],
        ]
    )


def get_client_back_kb() -> InlineKeyboardMarkup:
    """Return generic back button to client main menu."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💅 Записатися в Mini App",
                    web_app=WebAppInfo(url=settings.WEBAPP_URL),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="◀️ Назад до меню",
                    callback_data="client_main_menu",
                ),
            ],
        ]
    )
