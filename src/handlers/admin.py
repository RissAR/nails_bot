from datetime import date, datetime, time, timedelta
import html
import re

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.bot import notify_client_booking_status
from src.config import settings
from src.database.models.appointment import Appointment
from src.database.models.category import Category
from src.database.models.master import Master, MasterService
from src.database.models.service import Service
from src.database.models.user import User
from src.filters.admin import IsAdminFilter
from src.keyboards.admin_kb import (
    get_admin_back_kb,
    get_admin_categories_select_kb,
    get_admin_clients_list_kb,
    get_admin_clients_stats_kb,
    get_admin_main_kb,
    get_admin_masters_schedule_kb,
    get_admin_rejection_reasons_kb,
    get_admin_service_manage_kb,
    get_admin_services_kb,
)
from src.states import (
    AdminAddServiceFSM,
    AdminBlockSlotFSM,
    AdminDiscountFSM,
    AdminRejectFSM,
    AdminServiceFSM,
)

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

REJECTION_TEMPLATES = {
    "busy": "На жаль, на цей час майстер вже зайнятий або веде прийом іншого клієнта.",
    "sick": "На жаль, майстер раптово захворів(ла) та сьогодні не приймає.",
    "tech": "У студії заплановано технічну перерву (відсутність електроенергії/регламентні роботи).",
}

ADMIN_WELCOME_TEXT = (
    f"👑 <b>Панель керування студією «{settings.SALON_NAME}»</b>\n\n"
    "Тут ви можете оперативно керувати послугами (Live Sync), розкладом майстрів, "
    "обробляти заявки та керувати програмою лояльності клієнтів.\n\n"
    "Оберіть потрібний розділ:"
)


# =========================================================================
# 1. Main Navigation
# =========================================================================

@admin_router.message(Command("start"))
@admin_router.message(Command("admin"))
async def admin_start_handler(message: Message, state: FSMContext) -> None:
    """Handle admin /start or /admin command."""
    await state.clear()
    await message.answer(
        ADMIN_WELCOME_TEXT,
        reply_markup=get_admin_main_kb(),
    )


@admin_router.callback_query(F.data == "admin_main_menu")
async def admin_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """Return to admin main menu."""
    await state.clear()
    if callback.message:
        await callback.message.edit_text(
            ADMIN_WELCOME_TEXT,
            reply_markup=get_admin_main_kb(),
        )
    await callback.answer()


# =========================================================================
# 2. Service Management (Live Sync)
# =========================================================================

@admin_router.callback_query(F.data == "admin_services")
async def admin_services_callback(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    """Display interactive services management catalog."""
    await state.clear()
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
            "<i>Категорії відсутні. Перевірте сідінг бази даних.</i>"
        )
        markup = get_admin_back_kb()
    else:
        text = (
            f"📋 <b>Керування послугами «{settings.SALON_NAME}» (Live Sync):</b>\n\n"
            "🟢 — активна в Mini App та боті\n"
            "🔴 — вимкнена\n\n"
            "Натисніть на послугу нижче, щоб увімкнути/вимкнути її або змінити ціну:"
        )
        markup = get_admin_services_kb(categories)

    if callback.message:
        await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()


@admin_router.callback_query(F.data.startswith("adm_manage_srv:"))
async def admin_manage_service_callback(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    """Display detailed management card for a specific service."""
    try:
        service_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Помилка ідентифікатора послуги", show_alert=True)
        return

    stmt = (
        select(Service)
        .options(selectinload(Service.category), selectinload(Service.masters))
        .where(Service.id == service_id)
    )
    result = await session.execute(stmt)
    service = result.scalar_one_or_none()

    if not service:
        await callback.answer("Послугу не знайдено", show_alert=True)
        return

    status_str = "🟢 Активна (відображається в TMA та боті)" if service.is_active else "🔴 Вимкнена (прихована від клієнтів)"
    cat_name = service.category.name if service.category else "—"
    masters_str = ", ".join(m.name for m in service.masters) if service.masters else "Всі майстри"

    text = (
        f"💅 <b>Керування послугою:</b>\n\n"
        f"📌 <b>Назва:</b> {html.escape(service.name)}\n"
        f"📁 <b>Категорія:</b> {html.escape(cat_name)}\n"
        f"⏱ <b>Тривалість:</b> {service.duration_minutes} хв\n"
        f"💰 <b>Ціна:</b> {service.price:.0f} грн\n"
        f"🔘 <b>Статус:</b> {status_str}\n"
        f"👩‍🎨 <b>Майстри:</b> {html.escape(masters_str)}\n\n"
        "Оберіть дію:"
    )

    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=get_admin_service_manage_kb(service.id, service.is_active),
        )
    await callback.answer()


@admin_router.callback_query(F.data.startswith("adm_toggle_srv:"))
async def admin_toggle_service_callback(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    """Toggle service active status in DB (Live Sync)."""
    try:
        service_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Помилка ідентифікатора", show_alert=True)
        return

    service = await session.get(Service, service_id)
    if not service:
        await callback.answer("Послугу не знайдено", show_alert=True)
        return

    service.is_active = not service.is_active
    await session.commit()
    await session.refresh(service)

    alert_msg = f"Послугу «{service.name}» увімкнено!" if service.is_active else f"Послугу «{service.name}» вимкнено!"
    await callback.answer(alert_msg, show_alert=True)

    # Refresh card
    stmt = (
        select(Service)
        .options(selectinload(Service.category), selectinload(Service.masters))
        .where(Service.id == service_id)
    )
    result = await session.execute(stmt)
    refreshed_svc = result.scalar_one_or_none()
    if refreshed_svc and callback.message:
        status_str = "🟢 Активна (відображається в TMA та боті)" if refreshed_svc.is_active else "🔴 Вимкнена (прихована від клієнтів)"
        cat_name = refreshed_svc.category.name if refreshed_svc.category else "—"
        masters_str = ", ".join(m.name for m in refreshed_svc.masters) if refreshed_svc.masters else "Всі майстри"
        text = (
            f"💅 <b>Керування послугою:</b>\n\n"
            f"📌 <b>Назва:</b> {html.escape(refreshed_svc.name)}\n"
            f"📁 <b>Категорія:</b> {html.escape(cat_name)}\n"
            f"⏱ <b>Тривалість:</b> {refreshed_svc.duration_minutes} хв\n"
            f"💰 <b>Ціна:</b> {refreshed_svc.price:.0f} грн\n"
            f"🔘 <b>Статус:</b> {status_str}\n"
            f"👩‍🎨 <b>Майстри:</b> {html.escape(masters_str)}\n\n"
            "Оберіть дію:"
        )
        await callback.message.edit_text(
            text,
            reply_markup=get_admin_service_manage_kb(refreshed_svc.id, refreshed_svc.is_active),
        )


@admin_router.callback_query(F.data.startswith("adm_price_srv:"))
async def admin_price_service_callback(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    """Initiate price change FSM for a service."""
    try:
        service_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Помилка ідентифікатора", show_alert=True)
        return

    service = await session.get(Service, service_id)
    if not service:
        await callback.answer("Послугу не знайдено", show_alert=True)
        return

    await state.set_state(AdminServiceFSM.waiting_new_price)
    await state.update_data(service_id=service.id, service_name=service.name)

    if callback.message:
        await callback.message.edit_text(
            f"✏️ <b>Зміна ціни для «{html.escape(service.name)}»:</b>\n\n"
            f"Поточна ціна: <b>{service.price:.0f} грн</b>\n\n"
            "Введіть нову вартість у гривнях (число більше 0, наприклад: <code>600</code>):"
        )
    await callback.answer()


@admin_router.message(AdminServiceFSM.waiting_new_price)
async def admin_receive_new_price(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    """Handle new price input for service."""
    raw_text = (message.text or "").strip().replace(",", ".")
    try:
        new_price = float(raw_text)
        if new_price <= 0:
            raise ValueError()
    except ValueError:
        await message.answer(
            "⚠️ Будь ласка, введіть коректну ціну у вигляді додатного числа (наприклад: <code>600</code>):"
        )
        return

    data = await state.get_data()
    service_id = data.get("service_id")
    await state.clear()

    if not service_id:
        await message.answer("Сталася помилка сесії. Спробуйте знову через /admin.")
        return

    service = await session.get(Service, service_id)
    if not service:
        await message.answer("Послугу не знайдено в базі даних.")
        return

    old_price = service.price
    service.price = new_price
    await session.commit()

    await message.answer(
        f"✅ <b>Ціну для «{html.escape(service.name)}» успішно оновлено!</b>\n\n"
        f"Стара ціна: {old_price:.0f} грн\n"
        f"Нова ціна: <b>{new_price:.0f} грн</b>\n\n"
        "Зміни вже миттєво активні у Telegram Mini App та боті.",
        reply_markup=get_admin_back_kb(),
    )


@admin_router.callback_query(F.data == "adm_add_srv_start")
async def admin_add_service_start(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    """Start step-by-step FSM for adding a new service."""
    stmt = select(Category).order_by(Category.id)
    result = await session.execute(stmt)
    categories = list(result.scalars().all())

    if not categories:
        await callback.answer("Категорії відсутні в базі даних!", show_alert=True)
        return

    await state.set_state(AdminAddServiceFSM.waiting_category)
    if callback.message:
        await callback.message.edit_text(
            "➕ <b>Додавання нової послуги — Крок 1/4:</b>\n\n"
            "Оберіть категорію для нової послуги:",
            reply_markup=get_admin_categories_select_kb(categories),
        )
    await callback.answer()


@admin_router.callback_query(F.data.startswith("adm_add_srv_cat:"))
async def admin_add_service_cat_selected(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    """Handle category selection for new service."""
    try:
        cat_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Помилка категорії", show_alert=True)
        return

    category = await session.get(Category, cat_id)
    if not category:
        await callback.answer("Категорію не знайдено", show_alert=True)
        return

    await state.update_data(category_id=category.id, category_name=category.name)
    await state.set_state(AdminAddServiceFSM.waiting_name)

    if callback.message:
        await callback.message.edit_text(
            f"📁 Категорія: <b>{html.escape(category.name)}</b>\n\n"
            "➕ <b>Крок 2/4: Введіть назву послуги:</b>\n"
            "<i>(наприклад: SPA-педикюр з парафінотерапією)</i>"
        )
    await callback.answer()


@admin_router.message(AdminAddServiceFSM.waiting_name)
async def admin_add_service_name_received(
    message: Message,
    state: FSMContext,
) -> None:
    """Handle service name input."""
    name = (message.text or "").strip()
    if len(name) < 2 or len(name) > 100:
        await message.answer("⚠️ Назва має містити від 2 до 100 символів. Спробуйте ще раз:")
        return

    await state.update_data(name=name)
    await state.set_state(AdminAddServiceFSM.waiting_duration)
    await message.answer(
        f"📌 Назва: <b>{html.escape(name)}</b>\n\n"
        "➕ <b>Крок 3/4: Введіть тривалість процедури у хвилинах:</b>\n"
        "<i>(наприклад: 60, 90, 120)</i>"
    )


@admin_router.message(AdminAddServiceFSM.waiting_duration)
async def admin_add_service_duration_received(
    message: Message,
    state: FSMContext,
) -> None:
    """Handle service duration input."""
    try:
        duration = int((message.text or "").strip())
        if duration <= 0 or duration > 360:
            raise ValueError()
    except ValueError:
        await message.answer("⚠️ Введіть коректну тривалість від 5 до 360 хвилин:")
        return

    await state.update_data(duration_minutes=duration)
    await state.set_state(AdminAddServiceFSM.waiting_price)
    await message.answer(
        f"⏱ Тривалість: <b>{duration} хв</b>\n\n"
        "➕ <b>Крок 4/4: Введіть вартість послуги в гривнях:</b>\n"
        "<i>(наприклад: 650)</i>"
    )


@admin_router.message(AdminAddServiceFSM.waiting_price)
async def admin_add_service_price_received(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    """Finalize adding new service."""
    raw_text = (message.text or "").strip().replace(",", ".")
    try:
        price = float(raw_text)
        if price <= 0:
            raise ValueError()
    except ValueError:
        await message.answer("⚠️ Введіть коректну ціну у гривнях (додатне число):")
        return

    data = await state.get_data()
    await state.clear()

    cat_id = data.get("category_id")
    name = data.get("name")
    duration = data.get("duration_minutes", 60)

    # Create service
    new_service = Service(
        category_id=cat_id,
        name=name,
        duration_minutes=duration,
        price=price,
        is_active=True,
    )
    session.add(new_service)
    await session.flush()

    # Link all active masters by default
    m_stmt = select(Master).where(Master.is_active == True)  # noqa: E712
    m_res = await session.execute(m_stmt)
    active_masters = m_res.scalars().all()
    for m in active_masters:
        session.add(MasterService(master_id=m.id, service_id=new_service.id))

    await session.commit()

    await message.answer(
        f"🎉 <b>Нову послугу успішно створено!</b>\n\n"
        f"📌 <b>{html.escape(name)}</b>\n"
        f"⏱ Тривалість: {duration} хв\n"
        f"💰 Ціна: <b>{price:.0f} грн</b>\n"
        f"🔘 Статус: 🟢 Активна (Live Sync)\n\n"
        "Послуга вже доступна для онлайн-запису в Mini App!",
        reply_markup=get_admin_back_kb(),
    )


# =========================================================================
# 3. Masters & Schedule Management
# =========================================================================

@admin_router.callback_query(F.data == "admin_masters_schedule")
async def admin_masters_schedule_callback(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    """Display interactive masters schedule and management controls."""
    await state.clear()
    stmt = (
        select(Master)
        .options(selectinload(Master.schedules))
        .order_by(Master.id)
    )
    result = await session.execute(stmt)
    masters = list(result.scalars().all())

    text_lines = [
        f"👩‍🎨 <b>Керування розкладом майстрів «{settings.SALON_NAME}»:</b>\n",
        "Тут ви можете оперативно змінити статус прийому, встановити вихідний на завтра або додати перерву:\n",
    ]

    if not masters:
        text_lines.append("<i>Список майстрів порожній.</i>")
        markup = get_admin_back_kb()
    else:
        for m in masters:
            status_emoji = "🟢" if m.is_active else "🔴"
            status_text = "Приймає записи" if m.is_active else "Не приймає (прихована)"
            schedule_days = []
            hours = ""
            for sch in m.schedules:
                if not sch.is_day_off:
                    schedule_days.append(DAY_NAMES.get(sch.day_of_week, str(sch.day_of_week)))
                    hours = f"{sch.start_time.strftime('%H:%M')} – {sch.end_time.strftime('%H:%M')}"

            days_str = ", ".join(schedule_days) if schedule_days else "Немає графіку"
            full_sched = f"{days_str} ({hours})" if hours else days_str

            text_lines.append(
                f"{status_emoji} <b>{m.name}</b> ({m.title}) — <i>{status_text}</i>\n"
                f"   📅 Графік: {full_sched}\n"
            )
        markup = get_admin_masters_schedule_kb(masters)

    text = "\n".join(text_lines)
    if callback.message:
        await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()


@admin_router.callback_query(F.data.startswith("adm_toggle_mst:"))
async def admin_toggle_master_callback(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    """Toggle master active status in DB."""
    try:
        master_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Помилка ідентифікатора", show_alert=True)
        return

    master = await session.get(Master, master_id)
    if not master:
        await callback.answer("Майстра не знайдено", show_alert=True)
        return

    master.is_active = not master.is_active
    await session.commit()
    await session.refresh(master)

    msg = f"Майстриня {master.name} тепер приймає записи!" if master.is_active else f"Майстриня {master.name} тимчасово не приймає!"
    await callback.answer(msg, show_alert=True)

    # Refresh schedule view
    stmt = (
        select(Master)
        .options(selectinload(Master.schedules))
        .order_by(Master.id)
    )
    result = await session.execute(stmt)
    masters = list(result.scalars().all())

    text_lines = [
        f"👩‍🎨 <b>Керування розкладом майстрів «{settings.SALON_NAME}»:</b>\n",
        "Тут ви можете оперативно змінити статус прийому, встановити вихідний на завтра або додати перерву:\n",
    ]
    for m in masters:
        status_emoji = "🟢" if m.is_active else "🔴"
        status_text = "Приймає записи" if m.is_active else "Не приймає (прихована)"
        schedule_days = []
        hours = ""
        for sch in m.schedules:
            if not sch.is_day_off:
                schedule_days.append(DAY_NAMES.get(sch.day_of_week, str(sch.day_of_week)))
                hours = f"{sch.start_time.strftime('%H:%M')} – {sch.end_time.strftime('%H:%M')}"
        days_str = ", ".join(schedule_days) if schedule_days else "Немає графіку"
        full_sched = f"{days_str} ({hours})" if hours else days_str
        text_lines.append(
            f"{status_emoji} <b>{m.name}</b> ({m.title}) — <i>{status_text}</i>\n"
            f"   📅 Графік: {full_sched}\n"
        )
    if callback.message:
        await callback.message.edit_text(
            "\n".join(text_lines),
            reply_markup=get_admin_masters_schedule_kb(masters),
        )


@admin_router.callback_query(F.data.startswith("adm_dayoff_mst:"))
async def admin_set_dayoff_tomorrow_callback(
    callback: CallbackQuery,
    session: AsyncSession,
    db_user: User | None = None,
) -> None:
    """Set full day off tomorrow for a master by creating a blocking appointment."""
    try:
        master_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Помилка ідентифікатора", show_alert=True)
        return

    master = await session.get(Master, master_id)
    if not master:
        await callback.answer("Майстра не знайдено", show_alert=True)
        return

    tomorrow = date.today() + timedelta(days=1)

    # Check if existing block exists
    check_stmt = select(Appointment).where(
        Appointment.master_id == master.id,
        Appointment.booking_date == tomorrow,
        Appointment.status == "confirmed",
        Appointment.cancellation_reason == "Вихідний",
    )
    existing = await session.scalar(check_stmt)
    if existing:
        await callback.answer("Вихідний на завтра для цього майстра вже встановлено!", show_alert=True)
        return

    # Find a service to attach
    first_svc_stmt = select(Service).limit(1)
    first_svc = await session.scalar(first_svc_stmt)
    if not first_svc:
        await callback.answer("Послуги не знайдено", show_alert=True)
        return

    admin_client_id = db_user.id if db_user else 1

    block_apt = Appointment(
        client_id=admin_client_id,
        master_id=master.id,
        service_id=first_svc.id,
        booking_date=tomorrow,
        start_time=time(9, 0),
        end_time=time(20, 0),
        status="confirmed",
        cancellation_reason="Вихідний",
    )
    session.add(block_apt)
    await session.commit()

    await callback.answer(
        f"🛑 Встановлено вихідний на завтра ({tomorrow.strftime('%d.%m.%Y')}) для {master.name}! Всі слоти знято з Mini App.",
        show_alert=True,
    )


@admin_router.callback_query(F.data.startswith("adm_block_slot:"))
async def admin_block_slot_callback(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    """Initiate FSM to block specific hours / add break for a master."""
    try:
        master_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Помилка ідентифікатора", show_alert=True)
        return

    master = await session.get(Master, master_id)
    if not master:
        await callback.answer("Майстра не знайдено", show_alert=True)
        return

    await state.set_state(AdminBlockSlotFSM.waiting_range)
    await state.update_data(master_id=master.id, master_name=master.name)

    if callback.message:
        await callback.message.edit_text(
            f"⏸ <b>Додавання перерви / блоку годин для майстрині {html.escape(master.name)}:</b>\n\n"
            "Введіть дату та часовий діапазон у повідомленні.\n\n"
            "<i>Формати:</i>\n"
            "• <code>14:00-15:30</code> (на сьогодні)\n"
            "• <code>завтра 13:00-14:00</code>\n"
            "• <code>15.10.2026 10:00-12:00</code>\n\n"
            "Надішліть відповідь у чат:",
        )
    await callback.answer()


@admin_router.message(AdminBlockSlotFSM.waiting_range)
async def admin_block_slot_received(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    db_user: User | None = None,
) -> None:
    """Parse break range and persist blocking appointment."""
    text = (message.text or "").strip()
    data = await state.get_data()
    master_id = data.get("master_id")
    master_name = data.get("master_name", "Майстриня")
    await state.clear()

    # Regex matches: HH:MM-HH:MM or [date] HH:MM-HH:MM
    match = re.search(r"(\d{1,2}:\d{2})\s*[-–—]\s*(\d{1,2}:\d{2})", text)
    if not match:
        await message.answer(
            "⚠️ Не вдалося розпізнати діапазон часу. Формат має містити: <code>14:00-15:00</code>. Спробуйте знову через /admin."
        )
        return

    start_str, end_str = match.groups()
    try:
        sh, sm = map(int, start_str.split(":"))
        eh, em = map(int, end_str.split(":"))
        s_time = time(sh, sm)
        e_time = time(eh, em)
        if s_time >= e_time:
            raise ValueError()
    except Exception:
        await message.answer("⚠️ Некоректний час або час початку більший за кінець.")
        return

    # Determine date
    target_date = date.today()
    if "завтра" in text.lower():
        target_date = date.today() + timedelta(days=1)
    else:
        date_match = re.search(r"(\d{1,2})[.\-/](\d{1,2})(?:[.\-/](\d{2,4}))?", text)
        if date_match:
            try:
                day = int(date_match.group(1))
                month = int(date_match.group(2))
                year = int(date_match.group(3)) if date_match.group(3) else target_date.year
                if year < 100:
                    year += 2000
                target_date = date(year, month, day)
            except Exception:
                pass

    first_svc = await session.scalar(select(Service).limit(1))
    if not first_svc:
        await message.answer("Послуги не знайдено.")
        return

    admin_client_id = db_user.id if db_user else 1

    block_apt = Appointment(
        client_id=admin_client_id,
        master_id=master_id,
        service_id=first_svc.id,
        booking_date=target_date,
        start_time=s_time,
        end_time=e_time,
        status="confirmed",
        cancellation_reason="Технічна перерва / Блок годин",
    )
    session.add(block_apt)
    await session.commit()

    await message.answer(
        f"✅ <b>Технічну перерву встановлено!</b>\n\n"
        f"👩‍🎨 Майстер: <b>{master_name}</b>\n"
        f"📅 Дата: <b>{target_date.strftime('%d.%m.%Y')}</b>\n"
        f"⏰ Час: <b>{s_time.strftime('%H:%M')} – {e_time.strftime('%H:%M')}</b>\n\n"
        "Слоти у цей проміжок заблоковано в Mini App.",
        reply_markup=get_admin_back_kb(),
    )


# =========================================================================
# 4. Pending Appointments & Advanced Rejections with Reasons
# =========================================================================

@admin_router.callback_query(F.data == "admin_pending_appointments")
async def admin_pending_appointments_callback(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    """Display pending booking requests with approval/rejection triggers."""
    await state.clear()
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
            "<i>Наразі нових заявок немає. Всі записи оброблено!</i>"
        )
        if callback.message:
            await callback.message.edit_text(text, reply_markup=get_admin_back_kb())
        await callback.answer()
        return

    text_lines = [f"🔔 <b>Активні заявки на запис ({len(appointments)}):</b>\n"]
    for apt in appointments:
        client_name = apt.client.full_name if apt.client else "Невідомий"
        service_name = apt.service.name if apt.service else "Послуга"
        master_name = apt.master.name if apt.master else "Будь-який"
        phone = apt.client.phone if apt.client else "—"
        text_lines.append(
            f"🆔 <b>#{apt.id}</b> — {service_name}\n"
            f"   👤 {client_name} (📞 {phone})\n"
            f"   👩‍🎨 Майстер: {master_name}\n"
            f"   📅 {apt.booking_date.strftime('%d.%m.%Y')} о {apt.start_time.strftime('%H:%M')} – {apt.end_time.strftime('%H:%M')}\n"
        )
    text = "\n".join(text_lines)

    if callback.message:
        await callback.message.edit_text(text, reply_markup=get_admin_back_kb())
    await callback.answer()


@admin_router.callback_query(F.data.startswith("adm_appr:"))
async def admin_approve_booking_callback(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    """Handle admin booking confirmation inline button."""
    try:
        appointment_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Некоректний ID запису", show_alert=True)
        return

    stmt = (
        select(Appointment)
        .options(
            selectinload(Appointment.client),
            selectinload(Appointment.service),
            selectinload(Appointment.master),
        )
        .where(Appointment.id == appointment_id)
    )
    result = await session.execute(stmt)
    apt = result.scalar_one_or_none()

    if not apt:
        await callback.answer("Запис не знайдено!", show_alert=True)
        return

    if apt.status == "confirmed":
        await callback.answer("Заявку вже підтверджено!")
        return

    apt.status = "confirmed"
    # Loyalty update: increment completed visits and total spent
    if apt.client:
        apt.client.completed_visits += 1
        if apt.service:
            apt.client.total_spent += apt.service.price

    await session.commit()
    await session.refresh(apt)

    if callback.message:
        current_text = callback.message.html_text or callback.message.text or ""
        new_text = f"{current_text}\n\n✅ <b>ЗАЯВКУ ПІДТВЕРДЖЕНО</b>"
        new_markup = None
        if callback.message.reply_markup:
            remaining_rows = [
                row
                for row in callback.message.reply_markup.inline_keyboard
                if not any(
                    btn.callback_data
                    and (btn.callback_data.startswith("adm_appr:") or btn.callback_data.startswith("adm_rejc:"))
                    for btn in row
                )
            ]
            if remaining_rows:
                new_markup = InlineKeyboardMarkup(inline_keyboard=remaining_rows)

        try:
            await callback.message.edit_text(new_text, reply_markup=new_markup)
        except Exception:
            pass

    if apt.client and apt.client.telegram_id and apt.client.telegram_id > 0:
        try:
            await notify_client_booking_status(
                client_tg_id=apt.client.telegram_id,
                status="confirmed",
                service_name=apt.service.name if apt.service else "Послуга",
                master_name=apt.master.name if apt.master else "Майстер",
                booking_date=apt.booking_date.strftime("%d.%m.%Y"),
                start_time=apt.start_time.strftime("%H:%M"),
            )
        except Exception:
            pass

    await callback.answer("✅ Заявку успішно підтверджено!")


@admin_router.callback_query(F.data.startswith("adm_rejc:"))
async def admin_reject_booking_menu_callback(
    callback: CallbackQuery,
) -> None:
    """Prompt admin to select a rejection reason instead of instant deletion."""
    try:
        appointment_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Некоректний ID запису", show_alert=True)
        return

    text = (
        f"❓ <b>Оберіть причину відхилення заявки #{appointment_id} або напишіть свою:</b>\n\n"
        "Клієнту надійде ввічливе повідомлення з цією причиною та кнопкою для швидкого перебронювання."
    )
    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=get_admin_rejection_reasons_kb(appointment_id),
        )
    await callback.answer()


@admin_router.callback_query(F.data.startswith("adm_rej_reason:"))
async def admin_reject_with_template_callback(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    """Apply templated rejection reason, update DB, and notify client."""
    parts = callback.data.split(":")
    try:
        appointment_id = int(parts[1])
        reason_key = parts[2]
    except (IndexError, ValueError):
        await callback.answer("Помилка обробки", show_alert=True)
        return

    reason_text = REJECTION_TEMPLATES.get(
        reason_key,
        "Технічна перерва або майстер зайнятий на цей час.",
    )

    stmt = (
        select(Appointment)
        .options(
            selectinload(Appointment.client),
            selectinload(Appointment.service),
            selectinload(Appointment.master),
        )
        .where(Appointment.id == appointment_id)
    )
    result = await session.execute(stmt)
    apt = result.scalar_one_or_none()

    if not apt:
        await callback.answer("Запис не знайдено!", show_alert=True)
        return

    apt.status = "rejected"
    apt.cancellation_reason = reason_text
    await session.commit()
    await session.refresh(apt)

    if callback.message:
        new_text = (
            f"❌ <b>Заявку #{appointment_id} відхилено адміністратором</b>\n"
            f"💬 <b>Причина:</b> {html.escape(reason_text)}"
        )
        try:
            await callback.message.edit_text(new_text, reply_markup=get_admin_back_kb())
        except Exception:
            pass

    if apt.client and apt.client.telegram_id and apt.client.telegram_id > 0:
        try:
            await notify_client_booking_status(
                client_tg_id=apt.client.telegram_id,
                status="rejected",
                service_name=apt.service.name if apt.service else "Послуга",
                master_name=apt.master.name if apt.master else "Майстер",
                booking_date=apt.booking_date.strftime("%d.%m.%Y"),
                start_time=apt.start_time.strftime("%H:%M"),
                reason=reason_text,
            )
        except Exception:
            pass

    await callback.answer("❌ Заявку відхилено, клієнта сповіщено!")


@admin_router.callback_query(F.data.startswith("adm_rej_custom:"))
async def admin_reject_custom_start_callback(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Initiate FSM for typing a custom rejection reason."""
    try:
        appointment_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Помилка ID", show_alert=True)
        return

    await state.set_state(AdminRejectFSM.waiting_custom_reason)
    await state.update_data(appointment_id=appointment_id)

    if callback.message:
        await callback.message.edit_text(
            f"✍️ <b>Вкажіть власну причину відхилення для заявки #{appointment_id}:</b>\n\n"
            "Надішліть текст повідомленням у цей чат (клієнт отримає його в Telegram):"
        )
    await callback.answer()


@admin_router.message(AdminRejectFSM.waiting_custom_reason)
async def admin_reject_custom_received(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    """Handle custom rejection reason input, persist to DB, and notify client."""
    custom_reason = (message.text or "").strip()
    if len(custom_reason) < 3:
        await message.answer("⚠️ Причина має містити хоча б 3 символи. Введіть знову:")
        return

    data = await state.get_data()
    appointment_id = data.get("appointment_id")
    await state.clear()

    if not appointment_id:
        await message.answer("Сесія минула. Будь ласка, почніть через /admin.")
        return

    stmt = (
        select(Appointment)
        .options(
            selectinload(Appointment.client),
            selectinload(Appointment.service),
            selectinload(Appointment.master),
        )
        .where(Appointment.id == appointment_id)
    )
    result = await session.execute(stmt)
    apt = result.scalar_one_or_none()

    if not apt:
        await message.answer("Запис не знайдено.")
        return

    apt.status = "rejected"
    apt.cancellation_reason = custom_reason
    await session.commit()
    await session.refresh(apt)

    await message.answer(
        f"❌ <b>Заявку #{appointment_id} успішно відхилено.</b>\n\n"
        f"💬 <b>Причина:</b> {html.escape(custom_reason)}\n"
        "Клієнт отримав персоналізоване сповіщення у боті.",
        reply_markup=get_admin_back_kb(),
    )

    if apt.client and apt.client.telegram_id and apt.client.telegram_id > 0:
        try:
            await notify_client_booking_status(
                client_tg_id=apt.client.telegram_id,
                status="rejected",
                service_name=apt.service.name if apt.service else "Послуга",
                master_name=apt.master.name if apt.master else "Майстер",
                booking_date=apt.booking_date.strftime("%d.%m.%Y"),
                start_time=apt.start_time.strftime("%H:%M"),
                reason=custom_reason,
            )
        except Exception:
            pass


# =========================================================================
# 5. Clients & Loyalty Program Management
# =========================================================================

@admin_router.callback_query(F.data == "admin_clients_stats")
async def admin_clients_stats_callback(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    """Display registered clients statistics and loyalty entry button."""
    await state.clear()
    clients_count = await session.scalar(
        select(func.count(User.id)).where(User.role == "client")
    ) or 0
    total_users = await session.scalar(select(func.count(User.id))) or 0
    admins_count = await session.scalar(
        select(func.count(User.id)).where(User.role == "admin")
    ) or 0

    vip_count = await session.scalar(
        select(func.count(User.id)).where(User.role == "client", User.completed_visits >= 7)
    ) or 0
    regular_count = await session.scalar(
        select(func.count(User.id)).where(
            User.role == "client",
            User.completed_visits >= 3,
            User.completed_visits < 7,
        )
    ) or 0

    text = (
        f"📊 <b>Клієнти та програма лояльності «{settings.SALON_NAME}»:</b>\n\n"
        f"👥 Зареєстровані клієнти: <b>{clients_count}</b>\n"
        f"⭐ VIP-клієнти (7+ візитів, -10%): <b>{vip_count}</b>\n"
        f"💎 Постійні клієнти (3-6 візитів, -5%): <b>{regular_count}</b>\n"
        f"👑 Адміністратори: <b>{admins_count}</b>\n"
        f"📈 Загалом у базі: <b>{total_users}</b>\n\n"
        "Натисніть нижче для перегляду списку клієнтів та налаштування персональних знижок:"
    )

    if callback.message:
        await callback.message.edit_text(text, reply_markup=get_admin_clients_stats_kb())
    await callback.answer()


@admin_router.callback_query(F.data.startswith("adm_clients_list:"))
async def admin_clients_list_callback(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    """Display paginated list of studio clients with loyalty metrics."""
    try:
        page = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        page = 0

    page_size = 5
    total_clients = await session.scalar(
        select(func.count(User.id)).where(User.role == "client")
    ) or 0

    total_pages = max(1, (total_clients + page_size - 1) // page_size)
    if page >= total_pages:
        page = total_pages - 1

    stmt = (
        select(User)
        .where(User.role == "client")
        .order_by(User.completed_visits.desc(), User.id.desc())
        .offset(page * page_size)
        .limit(page_size)
    )
    result = await session.execute(stmt)
    clients = list(result.scalars().all())

    if not clients:
        text = "👥 <b>Список клієнтів:</b>\n\n<i>Клієнти ще не зареєстровані.</i>"
        markup = get_admin_back_kb()
    else:
        text_lines = [
            f"👥 <b>База клієнтів та лояльність (Стор. {page + 1}/{total_pages}):</b>\n"
        ]
        for c in clients:
            tier_name, discount = c.loyalty_info
            username_str = f"(@{c.username})" if c.username else ""
            phone_str = c.phone or "Телефон не вказано"
            text_lines.append(
                f"👤 <b>{html.escape(c.full_name)}</b> {username_str}\n"
                f"   📞 {phone_str}\n"
                f"   💅 Візитів: <b>{c.completed_visits}</b> | Сума: <b>{c.total_spent:.0f} грн</b>\n"
                f"   🏷 Рівень: <b>{tier_name}</b> (знижка <b>{discount}%</b>)\n"
            )
        text = "\n".join(text_lines)
        markup = get_admin_clients_list_kb(clients, page, total_pages)

    if callback.message:
        await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()


@admin_router.callback_query(F.data.startswith("adm_set_discount:"))
async def admin_set_discount_callback(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    """Initiate FSM to assign custom discount percentage to a client."""
    try:
        user_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Помилка користувача", show_alert=True)
        return

    client = await session.get(User, user_id)
    if not client:
        await callback.answer("Клієнта не знайдено", show_alert=True)
        return

    await state.set_state(AdminDiscountFSM.waiting_discount)
    await state.update_data(client_id=client.id, client_name=client.full_name)

    tier_name, current_discount = client.loyalty_info
    if callback.message:
        await callback.message.edit_text(
            f"🎁 <b>Встановлення знижки для {html.escape(client.full_name)}:</b>\n\n"
            f"Поточний статус: {tier_name} (знижка {current_discount}%)\n"
            f"Ручна знижка: {client.discount_percent}%\n\n"
            "Введіть бажаний відсоток знижки (ціле число від 0 до 50, де 0 — автоматичний розрахунок за візитами):"
        )
    await callback.answer()


@admin_router.message(AdminDiscountFSM.waiting_discount)
async def admin_receive_discount(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    """Handle custom discount percentage input."""
    raw = (message.text or "").strip()
    try:
        discount = int(raw)
        if discount < 0 or discount > 50:
            raise ValueError()
    except ValueError:
        await message.answer("⚠️ Будь ласка, введіть ціле число від 0 до 50:")
        return

    data = await state.get_data()
    client_id = data.get("client_id")
    client_name = data.get("client_name", "Клієнт")
    await state.clear()

    if not client_id:
        await message.answer("Помилка сесії. Спробуйте через /admin.")
        return

    client = await session.get(User, client_id)
    if not client:
        await message.answer("Клієнта не знайдено в базі даних.")
        return

    client.discount_percent = discount
    await session.commit()

    tier_name, effective_discount = client.loyalty_info
    await message.answer(
        f"✅ <b>Знижку для «{html.escape(client_name)}» збережено!</b>\n\n"
        f"Фіксована персональна знижка: <b>{discount}%</b>\n"
        f"Підсумкова ефективна знижка: <b>{effective_discount}%</b> ({tier_name})\n\n"
        "Ця знижка автоматично враховуватиметься при бронюванні в Mini App.",
        reply_markup=get_admin_back_kb(),
    )


# =========================================================================
# 6. WebApp Warning Fallback
# =========================================================================

@admin_router.callback_query(F.data == "admin_webapp_http_warning")
async def admin_webapp_http_warning_callback(callback: CallbackQuery) -> None:
    """Inform admin that Telegram WebApp requires HTTPS tunnel."""
    text = (
        "⚠️ <b>Адмін-панель TMA потребує HTTPS-з'єднання!</b>\n\n"
        f"Поточна адреса у конфігурації: <code>{settings.get_webapp_url({'role': 'admin'})}</code>\n\n"
        "📱 Telegram вимагає обов'язковий HTTPS протокол для запуску WebApp всередині месенджера.\n\n"
        "👉 <b>Як відкрити:</b>\n"
        f"1. Відкрийте у веб-браузері: {settings.get_webapp_url({'role': 'admin'})}\n"
        "2. Або запустіть тунель Cloudflare/ngrok і вкажіть його в <code>.env</code>."
    )
    if callback.message:
        await callback.message.edit_text(text, reply_markup=get_admin_back_kb())
    await callback.answer()
