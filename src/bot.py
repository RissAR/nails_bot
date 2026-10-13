import html
import logging
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.config import settings

logger = logging.getLogger(__name__)

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
) -> None:
    """Notify client about appointment status change (confirmed or rejected)."""
    if not client_tg_id or client_tg_id <= 0:
        return

    bot = get_bot()
    s_name = html.escape(service_name)
    m_name = html.escape(master_name)

    if status == "confirmed":
        text = (
            "✨ <b>Ваш запис підтверджено!</b>\n\n"
            f"💅 <b>Послуга:</b> {s_name}\n"
            f"👩‍🎨 <b>Майстер:</b> {m_name}\n"
            f"📅 <b>Дата:</b> {booking_date} о {start_time}\n"
            "📍 <b>Локація:</b> м. Івано-Франківськ, вул. Січових Стрільців\n\n"
            "Чекаємо на вас у Sense Nail Studio! Якщо ваші плани зміняться, будь ласка, попередьте нас завчасно."
        )
    elif status == "rejected":
        text = (
            f"😔 <b>На жаль, ваш запис на {booking_date} о {start_time} відхилено адміністратором.</b>\n\n"
            "Можливо, на цей час заплановано технічну перерву або майстер зайнятий.\n"
            f"Будь ласка, оберіть інший зручний час у Mini App або зв'яжіться з нами: {settings.ADMIN_USERNAME}."
        )
    else:
        return

    try:
        await bot.send_message(chat_id=client_tg_id, text=text)
        logger.info("Sent %s notification to client %d", status, client_tg_id)
    except Exception as e:
        logger.error("Failed to notify client %d about %s: %s", client_tg_id, status, e)
