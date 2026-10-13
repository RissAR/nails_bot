from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.config import settings
from src.database.models.appointment import Appointment
from src.database.models.category import Category
from src.database.models.master import Master
from src.database.models.user import User
from src.filters.admin import IsAdminFilter
from src.keyboards.admin_kb import get_admin_back_kb, get_admin_main_kb

admin_router = Router(name="admin_router")
admin_router.message.filter(IsAdminFilter())
admin_router.callback_query.filter(IsAdminFilter())

DAY_NAMES = {
    0: "Пн",
    1: "Вт",
    2: "Ср",
    3: "Чт",
    4: "Пт",
    5: "Сб",
    6: "Нд",
}

ADMIN_WELCOME_TEXT = (
    f"👑 <b>Панель керування студією «{settings.SALON_NAME}»</b>\n\n"
    "Тут ви можете оперативно переглядати структуру послуг, розклад майстрів, "
    "статистику зареєстрованих клієнтів та чергу заявок на запис.\n\n"
    "Оберіть потрібний розділ:"
)


@admin_router.message(Command("start"))
@admin_router.message(Command("admin"))
async def admin_start_handler(message: Message, db_user: User | None = None) -> None:
    """Handle admin /start or /admin command."""
    await message.answer(
        ADMIN_WELCOME_TEXT,
        reply_markup=get_admin_main_kb(),
    )


@admin_router.callback_query(F.data == "admin_main_menu")
async def admin_menu_callback(callback: CallbackQuery) -> None:
    """Return to admin main menu."""
    if callback.message:
        await callback.message.edit_text(
            ADMIN_WELCOME_TEXT,
            reply_markup=get_admin_main_kb(),
        )
    await callback.answer()


@admin_router.callback_query(F.data == "admin_services")
async def admin_services_callback(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    """Display active services grouped by categories."""
    stmt = (
        select(Category)
        .options(selectinload(Category.services))
        .order_by(Category.id)
    )
    result = await session.execute(stmt)
    categories = list(result.scalars().all())

    if not categories:
        text = (
            "📋 <b>Каталог послуг у базі даних:</b>\n\n"
            "<i>Категорії та послуги відсутні. Перевірте сідінг бази даних.</i>"
        )
    else:
        text_lines = [f"📋 <b>Каталог послуг «{settings.SALON_NAME}»:</b>\n"]
        for cat in categories:
            text_lines.append(f"📁 <b>{cat.name}</b>:")
            active_services = [s for s in cat.services if s.is_active]
            if not active_services:
                text_lines.append("   <i>(немає активних послуг)</i>")
            else:
                for s in active_services:
                    text_lines.append(
                        f"   • <b>{s.name}</b> — {s.duration_minutes} хв / {s.price:.0f} грн"
                    )
            text_lines.append("")
        text = "\n".join(text_lines)

    if callback.message:
        await callback.message.edit_text(text, reply_markup=get_admin_back_kb())
    await callback.answer()


@admin_router.callback_query(F.data == "admin_masters_schedule")
async def admin_masters_schedule_callback(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    """Display masters status and working schedules."""
    stmt = (
        select(Master)
        .options(selectinload(Master.schedules))
        .order_by(Master.id)
    )
    result = await session.execute(stmt)
    masters = list(result.scalars().all())

    text_lines = [f"👩‍🎨 <b>Майстри та розклад «{settings.SALON_NAME}»:</b>\n"]

    if not masters:
        text_lines.append("<i>Список майстрів порожній.</i>")
    else:
        for m in masters:
            status_emoji = "🟢" if m.is_active else "🔴"
            schedule_days = []
            hours = ""
            for sch in m.schedules:
                if not sch.is_day_off:
                    schedule_days.append(DAY_NAMES.get(sch.day_of_week, str(sch.day_of_week)))
                    hours = f"{sch.start_time.strftime('%H:%M')} – {sch.end_time.strftime('%H:%M')}"

            days_str = ", ".join(schedule_days) if schedule_days else "Немає фіксованих днів"
            full_sched = f"{days_str} ({hours})" if hours else days_str

            text_lines.append(
                f"{status_emoji} <b>{m.name}</b> ({m.title})\n"
                f"   📅 Графік: {full_sched}\n"
            )

    text = "\n".join(text_lines)
    if callback.message:
        await callback.message.edit_text(text, reply_markup=get_admin_back_kb())
    await callback.answer()


@admin_router.callback_query(F.data == "admin_pending_appointments")
async def admin_pending_appointments_callback(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    """Display pending booking requests."""
    stmt = (
        select(Appointment)
        .options(
            selectinload(Appointment.client),
            selectinload(Appointment.service),
            selectinload(Appointment.master),
        )
        .where(Appointment.status == "pending")
        .order_by(Appointment.booking_date, Appointment.start_time)
    )
    result = await session.execute(stmt)
    appointments = list(result.scalars().all())

    if not appointments:
        text = (
            "🔔 <b>Активні заявки на запис:</b>\n\n"
            "<i>Наразі нових заявок немає. Онлайн-запис розгортається для Mini App.</i>"
        )
    else:
        text_lines = ["🔔 <b>Активні заявки на запис:</b>\n"]
        for apt in appointments:
            client_name = apt.client.full_name if apt.client else "Невідомий"
            service_name = apt.service.name if apt.service else "Послуга"
            master_name = apt.master.name if apt.master else "Будь-який"
            text_lines.append(
                f"🆔 #{apt.id} — <b>{service_name}</b>\n"
                f"   👤 Клієнт: {client_name}\n"
                f"   💅 Майстер: {master_name}\n"
                f"   📅 Дата: {apt.booking_date.strftime('%d.%m.%Y')}\n"
                f"   ⏰ Час: {apt.start_time.strftime('%H:%M')} – {apt.end_time.strftime('%H:%M')}\n"
            )
        text = "\n".join(text_lines)

    if callback.message:
        await callback.message.edit_text(text, reply_markup=get_admin_back_kb())
    await callback.answer()


@admin_router.callback_query(F.data == "admin_clients_stats")
async def admin_clients_stats_callback(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    """Display registered client and system statistics."""
    clients_count = await session.scalar(
        select(func.count(User.id)).where(User.role == "client")
    ) or 0
    total_users = await session.scalar(select(func.count(User.id))) or 0
    admins_count = await session.scalar(
        select(func.count(User.id)).where(User.role == "admin")
    ) or 0

    text = (
        f"📊 <b>Статистика користувачів «{settings.SALON_NAME}»:</b>\n\n"
        f"👥 Зареєстровані клієнти: <b>{clients_count}</b>\n"
        f"👑 Адміністратори: <b>{admins_count}</b>\n"
        f"📈 Загальна кількість користувачів у системі: <b>{total_users}</b>\n\n"
        "<i>Користувачі автоматично фіксуються в БД при взаємодії з ботом.</i>"
    )

    if callback.message:
        await callback.message.edit_text(text, reply_markup=get_admin_back_kb())
    await callback.answer()


@admin_router.callback_query(F.data == "admin_webapp_http_warning")
async def admin_webapp_http_warning_callback(callback: CallbackQuery) -> None:
    """Inform admin that Telegram WebApp requires HTTPS tunnel."""
    text = (
        "⚠️ <b>Адмін-панель TMA потребує HTTPS-з'єднання!</b>\n\n"
        f"Поточна адреса у конфігурації: <code>{settings.WEBAPP_URL}?role=admin</code>\n\n"
        "📱 Telegram вимагає обов'язковий HTTPS протокол для запуску WebApp всередині месенджера.\n\n"
        "👉 <b>Як відкрити:</b>\n"
        f"1. Відкрийте у веб-браузері: {settings.WEBAPP_URL}?role=admin\n"
        "2. Або запустіть тунель Cloudflare/ngrok і вкажіть його в <code>.env</code>."
    )
    if callback.message:
        await callback.message.edit_text(text, reply_markup=get_admin_back_kb())
    await callback.answer()

