from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.config import settings
from src.database.models.category import Category
from src.database.models.master import Master
from src.database.models.service import Service
from src.database.models.user import User
from src.keyboards.client_kb import (
    get_categories_kb,
    get_category_services_kb,
    get_client_back_kb,
    get_client_main_kb,
)

client_router = Router(name="client_router")

DAY_NAMES = {
    0: "Пн",
    1: "Вт",
    2: "Ср",
    3: "Чт",
    4: "Пт",
    5: "Сб",
    6: "Нд",
}

CLIENT_WELCOME_TEXT = (
    f"✨ <b>Вітаємо у студії естетичного манікюру «{settings.SALON_NAME}»!</b> ✨\n\n"
    "Простір, де манікюр — це відчуття доглянутості, спокою та бездоганної естетики. "
    "Ми дотримуємося медичних стандартів стерильності (сухожар, крафт-пакети) "
    "та працюємо виключно на преміальних матеріалах.\n\n"
    "📍 <b>Локація:</b> м. Івано-Франківськ, центр, вул. Січових Стрільців\n"
    "🕒 <b>Графік роботи:</b> Щодня з 09:00 до 20:00\n\n"
    "Оберіть потрібний розділ для перегляду:"
)


@client_router.message(Command("start"))
async def client_start_handler(message: Message, db_user: User | None = None) -> None:
    """Handle /start command for clients."""
    await message.answer(
        CLIENT_WELCOME_TEXT,
        reply_markup=get_client_main_kb(),
    )


@client_router.callback_query(F.data == "client_main_menu")
async def client_main_menu_callback(callback: CallbackQuery) -> None:
    """Return to client main menu."""
    if callback.message:
        await callback.message.edit_text(
            CLIENT_WELCOME_TEXT,
            reply_markup=get_client_main_kb(),
        )
    await callback.answer()


@client_router.callback_query(F.data == "client_services")
async def client_services_callback(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    """Display interactive categories from the database."""
    stmt = select(Category).order_by(Category.id)
    result = await session.execute(stmt)
    categories = list(result.scalars().all())

    if not categories:
        text = "💅 <b>Каталог послуг:</b>\n\n<i>Каталог наразі оновлюється адміністратором.</i>"
        if callback.message:
            await callback.message.edit_text(text, reply_markup=get_client_back_kb())
        await callback.answer()
        return

    text = (
        f"💅 <b>Каталог послуг {settings.SALON_NAME}:</b>\n\n"
        "Оберіть категорію нижче, щоб переглянути детальний опис, тривалість та ціни:"
    )
    if callback.message:
        await callback.message.edit_text(text, reply_markup=get_categories_kb(categories))
    await callback.answer()


@client_router.callback_query(F.data.startswith("client_cat:"))
async def client_category_details_callback(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    """Display services for the selected category."""
    try:
        category_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Помилка навігації", show_alert=True)
        return

    cat_stmt = select(Category).where(Category.id == category_id)
    cat_result = await session.execute(cat_stmt)
    category = cat_result.scalar_one_or_none()

    if not category:
        await callback.answer("Категорію не знайдено", show_alert=True)
        return

    stmt = (
        select(Service)
        .options(selectinload(Service.masters))
        .where(Service.category_id == category_id, Service.is_active == True)  # noqa: E712
        .order_by(Service.price)
    )
    result = await session.execute(stmt)
    services = list(result.scalars().all())

    text_lines = [f"📂 <b>{category.name}</b>"]
    if not services:
        text_lines.append("<i>У цій категорії поки немає активних послуг.</i>")
    else:
        for s in services:
            line = f"• <b>{s.name}</b> — {s.price:.0f} грн ({s.duration_minutes} хв)"
            if s.description:
                line += f"\n  <i>{s.description}</i>"
            text_lines.append(line)

    text = "\n\n".join(text_lines)
    if callback.message:
        await callback.message.edit_text(text, reply_markup=get_category_services_kb(services))
    await callback.answer()


@client_router.callback_query(F.data == "client_masters")
async def client_masters_callback(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    """Display cards of salon masters with bios and schedules."""
    stmt = (
        select(Master)
        .options(selectinload(Master.schedules))
        .where(Master.is_active == True)  # noqa: E712
        .order_by(Master.id)
    )
    result = await session.execute(stmt)
    masters = list(result.scalars().all())

    text_lines = [f"👩‍🎨 <b>Команда майстрів {settings.SALON_NAME}:</b>\n"]
    if not masters:
        text_lines.append("<i>Інформація про майстрів оновлюється.</i>")
    else:
        for m in masters:
            schedule_days = []
            hours = ""
            for sch in m.schedules:
                if not sch.is_day_off:
                    schedule_days.append(DAY_NAMES.get(sch.day_of_week, str(sch.day_of_week)))
                    hours = f"{sch.start_time.strftime('%H:%M')} – {sch.end_time.strftime('%H:%M')}"

            days_str = ", ".join(schedule_days) if schedule_days else "За домовленістю"
            schedule_info = f"{days_str} ({hours})" if hours else days_str

            text_lines.append(
                f"✨ <b>{m.name}</b> — <i>{m.title}</i>\n"
                f"ℹ️ {m.bio or 'Професійний майстер манікюру'}\n"
                f"📅 <b>Графік:</b> {schedule_info}\n"
            )

    text = "\n".join(text_lines)
    if callback.message:
        await callback.message.edit_text(text, reply_markup=get_client_back_kb())
    await callback.answer()


@client_router.callback_query(F.data == "client_booking_soon")
async def client_booking_soon_callback(callback: CallbackQuery) -> None:
    """Inform about upcoming Mini App online booking."""
    text = (
        f"📅 <b>Онлайн-запис до «{settings.SALON_NAME}»</b>\n\n"
        "🚀 <i>Готується наступний реліз:</i>\n"
        "Зовсім скоро прямо у цьому боті відкриється <b>Telegram Mini App</b>! "
        "Ви зможете зручно обрати майстра, процедуру, переглянути інтерактивний календар "
        "вільних віконець та забронювати візит за 30 секунд.\n\n"
        f"👉 Наразі для запису напишіть нашому адміністратору: {settings.ADMIN_USERNAME}"
    )
    if callback.message:
        await callback.message.edit_text(text, reply_markup=get_client_back_kb())
    await callback.answer()


@client_router.callback_query(F.data == "client_contacts")
async def client_contacts_callback(callback: CallbackQuery) -> None:
    """Display contacts and location."""
    text = (
        f"📍 <b>Контакти студії «{settings.SALON_NAME}»:</b>\n\n"
        "🏢 <b>Адреса:</b> м. Івано-Франківськ, центр міста, вул. Січових Стрільців\n"
        "🕒 <b>Графік роботи:</b> Щодня з 09:00 до 20:00\n"
        f"💬 <b>Адміністратор для запису:</b> {settings.ADMIN_USERNAME}\n"
        "🛡 <b>Безпека:</b> 100% стерильність за медичними нормами (сухожар, сертифіковані крафт-пакети)"
    )
    if callback.message:
        await callback.message.edit_text(text, reply_markup=get_client_back_kb())
    await callback.answer()


@client_router.callback_query(F.data == "client_webapp_http_warning")
async def client_webapp_http_warning_callback(callback: CallbackQuery) -> None:
    """Inform user that Telegram WebApp requires HTTPS tunnel."""
    text = (
        "⚠️ <b>Telegram Mini App потребує HTTPS-з'єднання!</b>\n\n"
        f"Поточна адреса у конфігурації: <code>{settings.get_webapp_url()}</code>\n\n"
        "📱 Telegram не дозволяє відкривати WebApp через незахищений протокол <code>http://</code>.\n\n"
        "👉 <b>Як відкрити додаток:</b>\n"
        f"1. Відкрийте у браузері: {settings.get_webapp_url()}\n"
        "2. Або запустіть тунель Cloudflare/ngrok і додайте отриманий HTTPS URL у <code>.env</code>."
    )
    if callback.message:
        await callback.message.edit_text(text, reply_markup=get_client_back_kb())
    await callback.answer()

