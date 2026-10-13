from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models.appointment import Appointment
from src.database.models.master import Master
from src.database.models.service import Service
from src.database.models.user import User
from src.filters.admin import IsAdminFilter
from src.keyboards.admin_kb import get_admin_back_kb, get_admin_main_kb

admin_router = Router(name="admin_router")
admin_router.message.filter(IsAdminFilter())
admin_router.callback_query.filter(IsAdminFilter())


ADMIN_WELCOME_TEXT = (
    "👑 <b>Вітаємо в панелі керування салоном!</b>\n\n"
    "Оберіть потрібний розділ для керування:"
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
    """Display list of salon services."""
    stmt = select(Service).order_by(Service.id)
    result = await session.execute(stmt)
    services = result.scalars().all()

    if not services:
        text = (
            "📋 <b>Список послуг:</b>\n\n"
            "<i>Наразі жодної послуги не додано до бази даних.</i>"
        )
    else:
        text_lines = ["📋 <b>Список послуг салону:</b>\n"]
        for s in services:
            status_emoji = "✅" if s.is_active else "❌"
            text_lines.append(
                f"{status_emoji} <b>{s.name}</b>\n"
                f"   ⏱ Тривалість: {s.duration_minutes} хв.\n"
                f"   💰 Ціна: {s.price:.2f} грн\n"
            )
        text = "\n".join(text_lines)

    if callback.message:
        await callback.message.edit_text(text, reply_markup=get_admin_back_kb())
    await callback.answer()


@admin_router.callback_query(F.data == "admin_masters_schedule")
async def admin_masters_schedule_callback(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    """Display masters schedule placeholder and list."""
    stmt = select(Master).order_by(Master.id)
    result = await session.execute(stmt)
    masters = result.scalars().all()

    text_lines = [
        "📅 <b>Графік майстрів:</b>\n",
        "<i>(Попередній перегляд / повне керування буде доступно в Mini App)</i>\n",
    ]

    if not masters:
        text_lines.append("<i>Список майстрів наразі порожній.</i>")
    else:
        text_lines.append("<b>Зареєстровані майстри:</b>")
        for m in masters:
            status_emoji = "✅" if m.is_active else "❌"
            text_lines.append(f"• {status_emoji} {m.name}")

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
    appointments = result.scalars().all()

    if not appointments:
        text = (
            "🔔 <b>Активні заявки:</b>\n\n"
            "<i>Наразі немає активних заявок зі статусом 'pending'.</i>"
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
                f"   ⏰ Час: {apt.start_time.strftime('%H:%M')} - {apt.end_time.strftime('%H:%M')}\n"
            )
        text = "\n".join(text_lines)

    if callback.message:
        await callback.message.edit_text(text, reply_markup=get_admin_back_kb())
    await callback.answer()
