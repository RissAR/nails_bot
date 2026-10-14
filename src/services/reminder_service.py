import asyncio
from datetime import datetime, timedelta, timezone
import html
import logging
from zoneinfo import ZoneInfo

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from src.config import settings
from src.database.models import Appointment
from src.database.session import async_session_maker

logger = logging.getLogger(__name__)

KYIV_TZ = ZoneInfo("Europe/Kyiv")


async def process_24h_reminders(bot: Bot) -> None:
    """Send next-day (24 hours prior) reminders to confirmed clients."""
    now_kyiv = datetime.now(KYIV_TZ)
    today_kyiv = now_kyiv.date()
    tomorrow_kyiv = today_kyiv + timedelta(days=1)

    async with async_session_maker() as session:
        stmt = (
            select(Appointment)
            .options(
                selectinload(Appointment.client),
                selectinload(Appointment.service),
                selectinload(Appointment.master),
            )
            .where(
                Appointment.status == "confirmed",
                Appointment.reminded_24h == False,  # noqa: E712
            )
        )
        appointments = (await session.execute(stmt)).scalars().all()

        admin_contact = (
            f"@{settings.ADMIN_USERNAME.lstrip('@')}"
            if settings.ADMIN_USERNAME
            else "@andriy_bot_dev"
        )

        for apt in appointments:
            if apt.booking_date == tomorrow_kyiv:
                if apt.client and apt.client.telegram_id and apt.client.telegram_id > 0:
                    c_name = html.escape(apt.client.full_name or "Клієнте")
                    b_date_str = apt.booking_date.strftime("%d.%m.%Y")
                    s_time_str = apt.start_time.strftime("%H:%M")
                    svc_name = html.escape(apt.service.name if apt.service else "Послуга")
                    m_name = html.escape(apt.master.name if apt.master else "Майстер")

                    text = (
                        "✨ <b>Нагадування про завтрашній запис у Sense Nail Studio!</b>\n\n"
                        f"{c_name}, чекаємо на вас завтра (<b>{b_date_str}</b>) о <b>{s_time_str}</b>:\n"
                        f"💅 <b>Послуга:</b> {svc_name}\n"
                        f"👩‍🎨 <b>Майстер:</b> {m_name}\n"
                        "📍 <b>Адреса:</b> м. Івано-Франківськ, вул. Січових Стрільців\n\n"
                        f"Якщо ваші плани змінилися, будь ласка, повідомте адміністратора: {admin_contact}"
                    )

                    try:
                        await bot.send_message(
                            chat_id=apt.client.telegram_id,
                            text=text,
                            parse_mode=ParseMode.HTML,
                        )
                        logger.info("Sent 24h reminder for booking #%d to client %d", apt.id, apt.client.telegram_id)
                    except Exception as e:
                        logger.warning("Failed to send 24h reminder for #%d to client %d: %s", apt.id, apt.client.telegram_id, e)

                apt.reminded_24h = True
            elif apt.booking_date < tomorrow_kyiv:
                # Past or same-day appointment confirmed late, bypass 24h reminder
                apt.reminded_24h = True

        await session.commit()


async def process_2h_reminders(bot: Bot) -> None:
    """Send same-day (1.5 to 2.5 hours prior) reminders to confirmed clients."""
    now_kyiv = datetime.now(KYIV_TZ)
    today_kyiv = now_kyiv.date()

    async with async_session_maker() as session:
        stmt = (
            select(Appointment)
            .options(
                selectinload(Appointment.client),
                selectinload(Appointment.service),
                selectinload(Appointment.master),
            )
            .where(
                Appointment.status == "confirmed",
                Appointment.reminded_2h == False,  # noqa: E712
                Appointment.booking_date == today_kyiv,
            )
        )
        appointments = (await session.execute(stmt)).scalars().all()

        for apt in appointments:
            apt_dt = datetime.combine(apt.booking_date, apt.start_time, tzinfo=KYIV_TZ)
            diff = apt_dt - now_kyiv

            # Check if within 1.5 to 2.5 hours window
            if timedelta(minutes=90) <= diff <= timedelta(minutes=150):
                if apt.client and apt.client.telegram_id and apt.client.telegram_id > 0:
                    s_time_str = apt.start_time.strftime("%H:%M")
                    svc_name = html.escape(apt.service.name if apt.service else "Послуга")
                    m_name = html.escape(apt.master.name if apt.master else "Майстер")

                    text = (
                        f"⏳ <b>Чекаємо на вас сьогодні о {s_time_str}!</b>\n\n"
                        "Студія естетичного манікюру «Sense Nail Studio».\n"
                        f"💅 {svc_name} • Майстер: {m_name}\n"
                        "📍 вул. Січових Стрільців\n\n"
                        "Кава, чай та бездоганний манікюр уже чекають на вас ☕️✨"
                    )

                    try:
                        await bot.send_message(
                            chat_id=apt.client.telegram_id,
                            text=text,
                            parse_mode=ParseMode.HTML,
                        )
                        logger.info("Sent 2h reminder for booking #%d to client %d", apt.id, apt.client.telegram_id)
                    except Exception as e:
                        logger.warning("Failed to send 2h reminder for #%d to client %d: %s", apt.id, apt.client.telegram_id, e)

                apt.reminded_2h = True
            elif diff < timedelta(minutes=90):
                # Less than 1.5 hours remaining or already started
                apt.reminded_2h = True

        await session.commit()


async def process_pending_admin_alerts(bot: Bot) -> None:
    """Send reminder to admins about bookings pending for > 30 minutes."""
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    threshold_utc = now_utc - timedelta(minutes=30)

    async with async_session_maker() as session:
        stmt = (
            select(Appointment)
            .options(
                selectinload(Appointment.client),
                selectinload(Appointment.service),
            )
            .where(
                Appointment.status == "pending",
                Appointment.admin_alerted == False,  # noqa: E712
                Appointment.created_at <= threshold_utc,
            )
        )
        appointments = (await session.execute(stmt)).scalars().all()

        for apt in appointments:
            c_name = html.escape(apt.client.full_name if apt.client else "Гість")
            c_phone = html.escape(apt.client.phone if apt.client and apt.client.phone else "—")
            s_name = html.escape(apt.service.name if apt.service else "Послуга")
            s_time_str = apt.start_time.strftime("%H:%M")
            b_date_str = apt.booking_date.strftime("%d.%m.%Y")

            text = (
                f"⚠️ <b>Нагадування: Заявка #{apt.id} все ще очікує рішення!</b>\n"
                f"👤 Клієнт: {c_name} ({c_phone})\n"
                f"💅 Послуга: {s_name} о {s_time_str} ({b_date_str})\n"
                "Будь ласка, підтвердіть або відхиліть запис."
            )

            for admin_id in settings.ADMIN_IDS:
                try:
                    await bot.send_message(
                        chat_id=admin_id,
                        text=text,
                        parse_mode=ParseMode.HTML,
                    )
                    logger.info("Sent pending booking #%d reminder to admin %d", apt.id, admin_id)
                except Exception as e:
                    logger.warning("Failed to send pending reminder for #%d to admin %d: %s", apt.id, admin_id, e)

            apt.admin_alerted = True

        await session.commit()


async def process_feedback_requests(bot: Bot) -> None:
    """Send 5-star NPS rating request to clients 2 hours after visit completion."""
    now_kyiv = datetime.now(KYIV_TZ)

    async with async_session_maker() as session:
        stmt = (
            select(Appointment)
            .options(
                selectinload(Appointment.client),
                selectinload(Appointment.service),
                selectinload(Appointment.master),
            )
            .where(
                Appointment.status == "confirmed",
                Appointment.feedback_requested == False,  # noqa: E712
            )
        )
        appointments = (await session.execute(stmt)).scalars().all()

        for apt in appointments:
            apt_end_dt = datetime.combine(apt.booking_date, apt.end_time, tzinfo=KYIV_TZ)
            diff = now_kyiv - apt_end_dt

            if timedelta(hours=2) <= diff <= timedelta(hours=24):
                if apt.client and apt.client.telegram_id and apt.client.telegram_id > 0:
                    text = (
                        "💖 <b>Дякуємо, що завітали до Sense Nail Studio!</b>\n\n"
                        "Ми прагнемо, щоб кожен візит дарував вам відчуття комфорту та бездоганний результат.\n"
                        "Будь ласка, оцініть якість манікюру та обслуговування від 1 до 5 зірок:"
                    )
                    kb = InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(text="⭐ 1", callback_data=f"fb:{apt.id}:1"),
                                InlineKeyboardButton(text="⭐ 2", callback_data=f"fb:{apt.id}:2"),
                                InlineKeyboardButton(text="⭐ 3", callback_data=f"fb:{apt.id}:3"),
                                InlineKeyboardButton(text="⭐ 4", callback_data=f"fb:{apt.id}:4"),
                                InlineKeyboardButton(text="⭐ 5", callback_data=f"fb:{apt.id}:5"),
                            ]
                        ]
                    )
                    try:
                        await bot.send_message(
                            chat_id=apt.client.telegram_id,
                            text=text,
                            reply_markup=kb,
                            parse_mode=ParseMode.HTML,
                        )
                        logger.info("Sent feedback survey for booking #%d to client %d", apt.id, apt.client.telegram_id)
                    except Exception as e:
                        logger.warning("Failed to send feedback survey for #%d to client %d: %s", apt.id, apt.client.telegram_id, e)

                apt.feedback_requested = True
            elif diff > timedelta(hours=24):
                # Older than 24 hours, mark requested to avoid stale survey spam
                apt.feedback_requested = True

        await session.commit()


async def process_repeat_visit_reminders(bot: Bot) -> None:
    """Send repeat manicure reminder to clients ~21 days after previous visit (during 10:00-19:00)."""
    now_kyiv = datetime.now(KYIV_TZ)
    if not (10 <= now_kyiv.hour < 19):
        return

    today_kyiv = now_kyiv.date()

    async with async_session_maker() as session:
        stmt = (
            select(Appointment)
            .options(
                selectinload(Appointment.client),
                selectinload(Appointment.service),
            )
            .where(
                Appointment.status == "confirmed",
                Appointment.repeat_reminded == False,  # noqa: E712
                Appointment.booking_date <= today_kyiv - timedelta(days=21),
            )
        )
        appointments = (await session.execute(stmt)).scalars().all()

        for apt in appointments:
            if apt.booking_date < today_kyiv - timedelta(days=35):
                # Over 5 weeks old, bypass to prevent obsolete reminder spam
                apt.repeat_reminded = True
                continue

            # Check if client has future booking
            has_future = await session.scalar(
                select(func.count(Appointment.id)).where(
                    Appointment.client_id == apt.client_id,
                    Appointment.booking_date >= today_kyiv,
                    Appointment.status.in_(["pending", "confirmed"]),
                )
            )
            if has_future and has_future > 0:
                apt.repeat_reminded = True
                continue

            if apt.client and apt.client.telegram_id and apt.client.telegram_id > 0:
                c_name = html.escape(apt.client.full_name or "Клієнте")
                text = (
                    "💅 <b>Час оновити манікюр у Sense Nail Studio!</b> ✨\n\n"
                    f"{c_name}, минуло вже 3 тижні з вашого попереднього візиту.\n"
                    "Для підтримки ідеальної форми та здоров'я нігтиків рекомендується оновлювати покриття кожні 3–4 тижні.\n\n"
                    "Оберіть зручний час для наступного візиту у нашому онлайн-записі:"
                )
                is_https = settings.WEBAPP_URL.startswith("https://")
                if is_https:
                    tma_btn = InlineKeyboardButton(
                        text="💅 Записатися онлайн (Mini App)",
                        web_app=WebAppInfo(url=settings.get_webapp_url()),
                    )
                else:
                    tma_btn = InlineKeyboardButton(
                        text="💅 Записатися онлайн (Mini App)",
                        callback_data="client_webapp_http_warning",
                    )

                kb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [tma_btn],
                        [InlineKeyboardButton(text="🏠 Головне меню", callback_data="client_main_menu")],
                    ]
                )

                try:
                    await bot.send_message(
                        chat_id=apt.client.telegram_id,
                        text=text,
                        reply_markup=kb,
                        parse_mode=ParseMode.HTML,
                    )
                    logger.info("Sent 21-day repeat reminder for booking #%d to client %d", apt.id, apt.client.telegram_id)
                except Exception as e:
                    logger.warning("Failed to send 21-day repeat reminder for #%d to client %d: %s", apt.id, apt.client.telegram_id, e)

            apt.repeat_reminded = True

        await session.commit()


async def check_and_send_reminders(bot: Bot) -> None:
    """Execute all periodic reminder and alert checks."""
    try:
        await process_24h_reminders(bot)
    except Exception as e:
        logger.error("Error in process_24h_reminders: %s", e, exc_info=True)

    try:
        await process_2h_reminders(bot)
    except Exception as e:
        logger.error("Error in process_2h_reminders: %s", e, exc_info=True)

    try:
        await process_pending_admin_alerts(bot)
    except Exception as e:
        logger.error("Error in process_pending_admin_alerts: %s", e, exc_info=True)

    try:
        await process_feedback_requests(bot)
    except Exception as e:
        logger.error("Error in process_feedback_requests: %s", e, exc_info=True)

    try:
        await process_repeat_visit_reminders(bot)
    except Exception as e:
        logger.error("Error in process_repeat_visit_reminders: %s", e, exc_info=True)


async def run_reminder_worker(bot: Bot) -> None:
    """Background worker running every 60 seconds to process appointment reminders."""
    logger.info("Appointment reminder background worker started.")
    while True:
        try:
            await check_and_send_reminders(bot)
        except asyncio.CancelledError:
            logger.info("Appointment reminder worker cancelled.")
            break
        except Exception as e:
            logger.error("Unexpected error in reminder worker: %s", e, exc_info=True)

        try:
            await asyncio.sleep(60)
        except asyncio.CancelledError:
            logger.info("Appointment reminder worker cancelled during sleep.")
            break
