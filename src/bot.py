from datetime import date, datetime, time, timedelta, timezone
import html
import logging
import urllib.parse
from zoneinfo import ZoneInfo
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from src.config import settings

logger = logging.getLogger(__name__)

KYIV_TZ = ZoneInfo("Europe/Kyiv")

_bot: Bot | None = None


def get_bot() -> Bot:
    """Get or create singleton Bot instance."""
    global _bot
    if _bot is None:
        _bot = Bot(
            token=settings.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
    return _bot


def generate_google_calendar_url(
    service_name: str,
    master_name: str,
    booking_date_val: date | str,
    start_time_val: time | str,
    end_time_val: time | str | None = None,
    salon_name: str = "Sense Nail Studio",
    address: str = "м. Івано-Франківськ, вул. Січових Стрільців",
) -> str:
    """Generate direct Google Calendar event creation link."""
    if isinstance(booking_date_val, str):
        if "-" in booking_date_val:
            b_date = datetime.strptime(booking_date_val, "%Y-%m-%d").date()
        else:
            b_date = datetime.strptime(booking_date_val, "%d.%m.%Y").date()
    else:
        b_date = booking_date_val

    if isinstance(start_time_val, str):
        s_time = datetime.strptime(start_time_val, "%H:%M").time()
    else:
        s_time = start_time_val

    start_dt = datetime.combine(b_date, s_time, tzinfo=KYIV_TZ)
    if end_time_val:
        if isinstance(end_time_val, str):
            e_time = datetime.strptime(end_time_val, "%H:%M").time()
        else:
            e_time = end_time_val
        end_dt = datetime.combine(b_date, e_time, tzinfo=KYIV_TZ)
    else:
        end_dt = start_dt + timedelta(minutes=90)

    start_utc = start_dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    end_utc = end_dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    title = urllib.parse.quote(f"💅 {service_name} — {salon_name}")
    details = urllib.parse.quote(f"Запис до майстра {master_name}.\nСтудія: {salon_name}\nАдреса: {address}")
    location = urllib.parse.quote(address)

    return f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={title}&dates={start_utc}/{end_utc}&details={details}&location={location}"


async def notify_admins_new_booking(
    appointment_id: int,
    client_name: str,
    client_phone: str,
    client_tg_id: int | None,
    service_name: str,
    duration_minutes: int,
    price: float,
    master_name: str,
    booking_date: str,
    start_time: str,
    end_time: str,
    notes: str | None = None,
) -> None:
    """Send new booking card to all admins with inline action buttons."""
    bot = get_bot()

    # Escape HTML
    c_name = html.escape(client_name)
    c_phone = html.escape(client_phone)
    s_name = html.escape(service_name)
    m_name = html.escape(master_name)
    c_notes = html.escape(notes) if notes else "—"

    message_text = (
        f"🔔 <b>НОВА ЗАЯВКА НА ЗАПИС #{appointment_id}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Клієнт:</b> {c_name}\n"
        f"📞 <b>Телефон:</b> {c_phone}\n"
        f"💅 <b>Послуга:</b> {s_name} ({duration_minutes} хв, {price:.0f} грн)\n"
        f"👩‍🎨 <b>Майстер:</b> {m_name}\n"
        f"📅 <b>Дата:</b> {booking_date}\n"
        f"⏰ <b>Час:</b> {start_time} – {end_time}\n"
        f"💬 <b>Коментар:</b> {c_notes}"
    )

    action_buttons = [
        [
            InlineKeyboardButton(
                text="✅ Підтвердити",
                callback_data=f"adm_appr:{appointment_id}",
            ),
            InlineKeyboardButton(
                text="❌ Відхилити",
                callback_data=f"adm_rejc:{appointment_id}",
            ),
        ]
    ]

    if client_tg_id and client_tg_id > 0:
        action_buttons.append([
            InlineKeyboardButton(
                text="💬 Написати клієнту",
                url=f"tg://user?id={client_tg_id}",
            )
        ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=action_buttons)

    for admin_id in settings.ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=message_text,
                reply_markup=keyboard,
            )
            logger.info("Sent new booking notification #%d to admin %d", appointment_id, admin_id)
        except Exception as e:
            logger.error("Failed to notify admin %d about booking #%d: %s", admin_id, appointment_id, e)


async def notify_client_booking_status(
    client_tg_id: int | None,
    status: str,
    service_name: str,
    master_name: str,
    booking_date: str,
    start_time: str,
    end_time: str | None = None,
    reason: str | None = None,
) -> None:
    """Notify client about appointment status change (confirmed or rejected)."""
    if not client_tg_id or client_tg_id <= 0:
        return

    bot = get_bot()
    s_name = html.escape(service_name)
    m_name = html.escape(master_name)

    reply_markup = None
    if status == "confirmed":
        gcal_url = generate_google_calendar_url(
            service_name=service_name,
            master_name=master_name,
            booking_date_val=booking_date,
            start_time_val=start_time,
            end_time_val=end_time,
            salon_name=settings.SALON_NAME,
        )
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📅 Додати в Google Календар",
                        url=gcal_url,
                    )
                ]
            ]
        )
        text = (
            "✨ <b>Ваш запис підтверджено!</b>\n\n"
            f"💅 <b>Послуга:</b> {s_name}\n"
            f"👩‍🎨 <b>Майстер:</b> {m_name}\n"
            f"📅 <b>Дата:</b> {booking_date} о {start_time}\n"
            "📍 <b>Локація:</b> м. Івано-Франківськ, вул. Січових Стрільців\n\n"
            "Чекаємо на вас у Sense Nail Studio! Якщо ваші плани зміняться, будь ласка, попередьте нас завчасно."
        )
    elif status == "rejected":
        reason_text = html.escape(reason) if reason else "Технічна перерва або зайнятість майстра."
        text = (
            f"😔 <b>Ваш запис на {booking_date} о {start_time} скасовано</b>\n\n"
            f"<b>Причина:</b> {reason_text}\n\n"
            f"Будь ласка, оберіть інший зручний час у нашому Mini App або зв'яжіться з адміністратором: {settings.ADMIN_USERNAME}"
        )
        is_https = settings.WEBAPP_URL.startswith("https://")
        if is_https:
            btn = InlineKeyboardButton(
                text="💅 Обрати інший час (Mini App)",
                web_app=WebAppInfo(url=settings.get_webapp_url()),
            )
        else:
            btn = InlineKeyboardButton(
                text="💅 Обрати інший час (Mini App)",
                callback_data="client_webapp_http_warning",
            )
        reply_markup = InlineKeyboardMarkup(inline_keyboard=[[btn]])
    else:
        return

    try:
        await bot.send_message(chat_id=client_tg_id, text=text, reply_markup=reply_markup)
        logger.info("Sent %s notification to client %d", status, client_tg_id)
    except Exception as e:
        logger.error("Failed to notify client %d about %s: %s", client_tg_id, status, e)
