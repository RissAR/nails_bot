from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from src.database.models.user import User
from src.keyboards.client_kb import get_client_back_kb, get_client_main_kb

client_router = Router(name="client_router")


CLIENT_WELCOME_TEXT = (
    "✨ <b>Ласкаво просимо до нашого салону манікюру!</b> ✨\n\n"
    "Ми створюємо ідеальний манікюр з турботою про ваші нігтики. "
    "У нас ви знайдете бездоганну якість, 100% стерильність та затишну атмосферу.\n\n"
    "Оберіть дію в меню нижче:"
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


@client_router.callback_query(F.data == "client_booking_soon")
async def client_booking_soon_callback(callback: CallbackQuery) -> None:
    """Handle online booking button."""
    text = (
        "💅 <b>Онлайн-запис через Telegram Mini App</b>\n\n"
        "🚀 Зовсім скоро ви зможете зручно обрати майстра, бажану послугу, "
        "дату та вільний час безпосередньо у нашому боті через інтерактивний додаток!\n\n"
        "Слідкуйте за оновленнями або зв'яжіться з адміністратором у розділі Контакти."
    )
    if callback.message:
        await callback.message.edit_text(text, reply_markup=get_client_back_kb())
    await callback.answer()


@client_router.callback_query(F.data == "client_about")
async def client_about_callback(callback: CallbackQuery) -> None:
    """Handle about salon button."""
    text = (
        "ℹ️ <b>Про наш салон:</b>\n\n"
        "💎 <b>Професіоналізм:</b> Досвідчені топ-майстри зі стажем понад 5 років.\n"
        "🛡 <b>Безпека:</b> 3-етапна стерилізація інструментів (сухожар, крафт-пакети, дезінфекція).\n"
        "🌿 <b>Преміум матеріали:</b> Тільки сертифіковані та гіпоалергенні гель-лаки.\n"
        "☕️ <b>Комфорт:</b> Смачна кава, чай, солодощі та улюблені фільми під час процедури."
    )
    if callback.message:
        await callback.message.edit_text(text, reply_markup=get_client_back_kb())
    await callback.answer()


@client_router.callback_query(F.data == "client_contacts")
async def client_contacts_callback(callback: CallbackQuery) -> None:
    """Handle contacts button."""
    text = (
        "📞 <b>Контакти та локація:</b>\n\n"
        "📍 <b>Адреса:</b> м. Київ, вул. Центральна, 10 (м. Хрещатик)\n"
        "🕒 <b>Графік роботи:</b> Щодня з 09:00 до 21:00\n"
        "📱 <b>Телефон:</b> +380 (99) 123-45-67\n"
        "💬 <b>Telegram:</b> @andriy_bot_dev\n"
        "📸 <b>Instagram:</b> @nails_salon_kyiv"
    )
    if callback.message:
        await callback.message.edit_text(text, reply_markup=get_client_back_kb())
    await callback.answer()
