from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from src.config import settings
from src.database.models.category import Category
from src.database.models.service import Service


def get_client_main_kb() -> InlineKeyboardMarkup:
    """Return main client interactive inline keyboard with WebApp button."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💅 Записатися онлайн (Mini App)",
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
                text="💅 Відкрити Mini App",
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


def get_category_services_kb(services: list[Service] | None = None) -> InlineKeyboardMarkup:
    """Return keyboard with navigation and direct booking buttons for services."""
    buttons: list[list[InlineKeyboardButton]] = []

    if services:
        for s in services:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"✨ Запис: {s.name} ({s.price:.0f} грн)",
                        web_app=WebAppInfo(url=f"{settings.WEBAPP_URL}?service_id={s.id}"),
                    )
                ]
            )

    buttons.append(
        [
            InlineKeyboardButton(
                text="💅 Записатися в Mini App",
                web_app=WebAppInfo(url=settings.WEBAPP_URL),
            ),
        ]
    )
    buttons.append(
        [
            InlineKeyboardButton(
                text="◀️ До категорій",
                callback_data="client_services",
            ),
            InlineKeyboardButton(
                text="🏠 Головне меню",
                callback_data="client_main_menu",
            ),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_service_detail_kb(service_id: int, category_id: int | None = None) -> InlineKeyboardMarkup:
    """Return keyboard with direct Mini App deep link for a specific service."""
    back_callback = f"client_cat:{category_id}" if category_id else "client_services"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✨ Записатися на цю послугу",
                    web_app=WebAppInfo(url=f"{settings.WEBAPP_URL}?service_id={service_id}"),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="◀️ Назад до послуг",
                    callback_data=back_callback,
                ),
                InlineKeyboardButton(
                    text="🏠 Меню",
                    callback_data="client_main_menu",
                ),
            ],
        ]
    )


def get_client_back_kb() -> InlineKeyboardMarkup:
    """Return generic back button to client main menu with Mini App link."""
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
