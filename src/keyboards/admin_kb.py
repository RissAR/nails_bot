from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from src.config import settings


def get_admin_main_kb() -> InlineKeyboardMarkup:
    """Return main admin control panel inline keyboard with WebApp or safe fallback."""
    is_https = settings.WEBAPP_URL.startswith("https://")

    if is_https:
        tma_btn = InlineKeyboardButton(
            text="📱 Відкрити адмін-панель TMA",
            web_app=WebAppInfo(url=f"{settings.WEBAPP_URL}?role=admin"),
        )
    else:
        tma_btn = InlineKeyboardButton(
            text="📱 Відкрити адмін-панель TMA",
            callback_data="admin_webapp_http_warning",
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [tma_btn],
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
    is_https = settings.WEBAPP_URL.startswith("https://")

    if is_https:
        tma_btn = InlineKeyboardButton(
            text="📱 Відкрити адмін-панель TMA",
            web_app=WebAppInfo(url=f"{settings.WEBAPP_URL}?role=admin"),
        )
    else:
        tma_btn = InlineKeyboardButton(
            text="📱 Відкрити адмін-панель TMA",
            callback_data="admin_webapp_http_warning",
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [tma_btn],
            [
                InlineKeyboardButton(
                    text="◀️ Назад в адмін-панель",
                    callback_data="admin_main_menu",
                ),
            ],
        ]
    )


def get_admin_services_kb(categories: list) -> InlineKeyboardMarkup:
    """Return keyboard listing all categories and their services with management callbacks."""
    rows: list[list[InlineKeyboardButton]] = []

    for cat in categories:
        for s in cat.services:
            status_emoji = "🟢" if s.is_active else "🔴"
            rows.append([
                InlineKeyboardButton(
                    text=f"{status_emoji} {s.name} ({s.price:.0f} грн)",
                    callback_data=f"adm_manage_srv:{s.id}",
                )
            ])

    # Action buttons at the bottom
    rows.append([
        InlineKeyboardButton(
            text="➕ Додати нову послугу",
            callback_data="adm_add_srv_start",
        )
    ])
    rows.append([
        InlineKeyboardButton(
            text="◀️ Головне меню",
            callback_data="admin_main_menu",
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_admin_service_manage_kb(service_id: int, is_active: bool) -> InlineKeyboardMarkup:
    """Return actions for a specific service: toggle active, change price, back."""
    status_text = "🔴 Вимкнути послугу" if is_active else "🟢 Увімкнути послугу"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=status_text,
                    callback_data=f"adm_toggle_srv:{service_id}",
                ),
                InlineKeyboardButton(
                    text="✏️ Змінити ціну",
                    callback_data=f"adm_price_srv:{service_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="◀️ До списку послуг",
                    callback_data="admin_services",
                ),
                InlineKeyboardButton(
                    text="🏠 Головне меню",
                    callback_data="admin_main_menu",
                ),
            ],
        ]
    )


def get_admin_categories_select_kb(categories: list) -> InlineKeyboardMarkup:
    """Return category selection keyboard when adding a service."""
    rows = [
        [
            InlineKeyboardButton(
                text=f"📁 {cat.name}",
                callback_data=f"adm_add_srv_cat:{cat.id}",
            )
        ]
        for cat in categories
    ]
    rows.append([
        InlineKeyboardButton(
            text="◀️ Скасувати",
            callback_data="admin_services",
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_admin_masters_schedule_kb(masters: list) -> InlineKeyboardMarkup:
    """Return interactive management keyboard for masters status and day off."""
    rows: list[list[InlineKeyboardButton]] = []
    for m in masters:
        status_text = "🔴 Не приймає" if m.is_active else "🟢 Приймає"
        rows.append([
            InlineKeyboardButton(
                text=f"{m.name}: {status_text}",
                callback_data=f"adm_toggle_mst:{m.id}",
            ),
        ])
        rows.append([
            InlineKeyboardButton(
                text=f"🛑 Вихідний на завтра ({m.name})",
                callback_data=f"adm_dayoff_mst:{m.id}:tomorrow",
            ),
            InlineKeyboardButton(
                text=f"⏸ Додати перерву ({m.name})",
                callback_data=f"adm_block_slot:{m.id}",
            ),
        ])

    rows.append([
        InlineKeyboardButton(
            text="◀️ Головне меню",
            callback_data="admin_main_menu",
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_admin_rejection_reasons_kb(appointment_id: int) -> InlineKeyboardMarkup:
    """Return inline rejection reason choices for appointment."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⏳ Майстер зайнятий на цей час",
                    callback_data=f"adm_rej_reason:{appointment_id}:busy",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🤒 Майстер на лікарняному",
                    callback_data=f"adm_rej_reason:{appointment_id}:sick",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⚡️ Технічна перерва / Немає світла",
                    callback_data=f"adm_rej_reason:{appointment_id}:tech",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✍️ Вказати власну причину",
                    callback_data=f"adm_rej_custom:{appointment_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="◀️ Скасувати відхилення",
                    callback_data="admin_pending_appointments",
                ),
            ],
        ]
    )


def get_admin_clients_stats_kb() -> InlineKeyboardMarkup:
    """Return keyboard for clients stats overview."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👥 Список клієнтів та лояльність",
                    callback_data="adm_clients_list:0",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="◀️ Головне меню",
                    callback_data="admin_main_menu",
                ),
            ],
        ]
    )


def get_admin_clients_list_kb(clients: list, page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Return paginated list of clients with discount management buttons."""
    rows: list[list[InlineKeyboardButton]] = []
    for c in clients:
        display_name = c.full_name or f"User {c.telegram_id}"
        rows.append([
            InlineKeyboardButton(
                text=f"🎁 Знижка: {display_name}",
                callback_data=f"adm_set_discount:{c.id}",
            )
        ])

    nav_row: list[InlineKeyboardButton] = []
    if page > 0:
        nav_row.append(
            InlineKeyboardButton(
                text="⬅️ Попередня",
                callback_data=f"adm_clients_list:{page - 1}",
            )
        )
    if page < total_pages - 1:
        nav_row.append(
            InlineKeyboardButton(
                text="➡️ Наступна",
                callback_data=f"adm_clients_list:{page + 1}",
            )
        )
    if nav_row:
        rows.append(nav_row)

    rows.append([
        InlineKeyboardButton(
            text="◀️ До статистики",
            callback_data="admin_clients_stats",
        ),
        InlineKeyboardButton(
            text="🏠 Меню",
            callback_data="admin_main_menu",
        ),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)

