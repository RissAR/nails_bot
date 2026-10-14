# ТЕХНІЧНЕ ЗАВДАННЯ: Етап 11 — Заміна MenuButton на постійну Reply-кнопку «🏠 Головне меню» та впровадження автономних маркетингових функцій (Блок 3)

## 1. Загальна інформація та мета етапу
- **Мета:**
  1. **Очищення Telegram MenuButton та додавання постійної Reply-кнопки по центру:**
     - Прибрати з лівого нижнього кута меню Telegram кнопку «💅 Запис» (`MenuButtonWebApp`), яка створює зайвий візуальний шум і не використовується клієнтами.
     - Замість неї встановити дефолтний стан `MenuButtonDefault()`.
     - Додати постійну зручну кнопку `[ 🏠 Головне меню ]` по центру з самого-самого низу (`ReplyKeyboardMarkup` з параметрами `resize_keyboard=True` та `is_persistent=True`), щоб клієнт міг повернутися до головного меню в будь-який момент незалежно від попередніх дій або відкритих екранів.
     - Для адміністратора кнопка `[ 🏠 Головне меню ]` повинна миттєво повертати в панель керування адміністратора (`ADMIN_WELCOME_TEXT` + `get_admin_main_kb()`).
  2. **Автономні маркетингові функції та утримання клієнтів (Блок 3):**
     - **Збір NPS / Оцінка сервісу після візиту:** Через 2 години після фактичного закінчення візиту надсилати клієнту автоматичне опитування з 5 зірками `[ ⭐ 1 ] [ ⭐ 2 ] [ ⭐ 3 ] [ ⭐ 4 ] [ ⭐ 5 ]`. Високі оцінки (4-5) — подяка; низькі оцінки (1-3) — повідомлення з вибаченням та миттєвий алерт адміністраторам для відпрацювання негативу.
     - **Автоматичне нагадування про повторний візит (21 день):** Через 3 тижні після попереднього візиту у комфортний денний час (10:00–19:00) нагадувати клієнту про необхідність корекції/оновлення манікюру з прямою кнопкою відкриття Mini App (якщо у клієнта ще немає активного майбутнього запису).
     - **Посилання «Додати в Google Календар»:** При підтвердженні запису генерувати інлайн-кнопку з посиланням на Google Календар із точною датою, часом процедури, назвою послуги, майстром та адресою студії.
  3. **Перезапуск локального демона бота:**
     - Перезапустити процес `python -m src.main` у фоновому режимі (`nohup`) та зафіксувати коректну роботу в логах.
- **GitHub Repository:** `https://github.com/RissAR/nails_bot.git` (гілка `main`)
- **Стек:** Python 3.12, aiogram 3.x, SQLAlchemy 2.0 Async, SQLite.

---

## 2. Суворі правила безпеки та виконання (Strict Security & Scope Discipline)
1. **Zero Hardcoded Secrets (КРИТИЧНО):** `BOT_TOKEN` та інші конфіденційні дані зчитуються **виключно з локального `.env`**. Заборонено записувати токени у файли коду.
2. **Zero Scope Creep:** Модифікувати тільки файли, які стосуються меню, клавіатур, нагадувань, обробників відгуків та моделі записів (`src/main.py`, `src/keyboards/client_kb.py`, `src/handlers/client.py`, `src/handlers/admin.py`, `src/services/reminder_service.py`, `src/bot.py`, `src/database/models/appointment.py`, `src/database/init_db.py`).
3. **Збереження існуючої логіки:** Жодних заглушок (`// rest of code`). Усі існуючі обробники статусів, міграції та перевірки інтервалів зберігаються в повному обсязі.
4. **Git Автоматизація:** Після завершення роботи виконати:
   `git add . && git commit -m "feat: replace webapp menu button with main menu reply keyboard and add marketing automation" && git push origin main`.

---

## 3. Деталі технічної реалізації

### 3.1. Очищення MenuButton та впровадження постійної кнопки «🏠 Головне меню»

1. **`src/main.py`:**
   - Імпортувати `MenuButtonDefault` з `aiogram.types`.
   - Прибрати виклик `MenuButtonWebApp(text="💅 Запис", ...)` та встановити:
     ```python
     try:
         await bot.set_chat_menu_button(menu_button=MenuButtonDefault())
         logger.info("Chat menu button reset to default.")
     except Exception as e:
         logger.warning("Failed to reset chat menu button: %s", e)
     ```
   - Завдяки цьому з лівого нижнього кута прибирається зайва кнопка «💅 Запис».

2. **`src/keyboards/client_kb.py`:**
   - Імпортувати `KeyboardButton, ReplyKeyboardMarkup` з `aiogram.types`.
   - Створити функцію створення персистентної reply-клавіатури:
     ```python
     def get_client_reply_kb() -> ReplyKeyboardMarkup:
         """Return persistent single-button reply keyboard pinned at bottom center."""
         return ReplyKeyboardMarkup(
             keyboard=[[KeyboardButton(text="🏠 Головне меню")]],
             resize_keyboard=True,
             is_persistent=True,
         )
     ```

3. **`src/handlers/client.py`:**
   - У `client_start_handler`:
     При виклику `/start` клієнтом:
     - Очистити можливий FSM стан.
     - Надіслати коротке сервісне повідомлення для ініціалізації персистентної reply-клавіатури (або прикріпити її):
       ```python
       await message.answer(
           "👋 Для швидкої навігації використовуйте кнопку «🏠 Головне меню» внизу екрана.",
           reply_markup=get_client_reply_kb(),
       )
       await message.answer(
           CLIENT_WELCOME_TEXT,
           reply_markup=get_client_main_kb(),
       )
       ```
   - Додати обробник кнопки «🏠 Головне меню»:
     ```python
     @client_router.message(F.text.in_({"🏠 Головне меню", "Головне меню"}))
     async def client_main_menu_button_handler(message: Message, state: FSMContext | None = None) -> None:
         """Return client to main interactive menu."""
         if state:
             await state.clear()
         await message.answer(
             CLIENT_WELCOME_TEXT,
             reply_markup=get_client_main_kb(),
         )
     ```

4. **`src/handlers/admin.py`:**
   - Додати перехоплення `F.text.in_({"🏠 Головне меню", "Головне меню"})` для адміністраторів:
     ```python
     @admin_router.message(F.text.in_({"🏠 Головне меню", "Головне меню"}))
     @admin_router.message(Command("start"))
     @admin_router.message(Command("admin"))
     async def admin_start_handler(message: Message, state: FSMContext) -> None:
         """Handle admin start or main menu button."""
         await state.clear()
         await message.answer(
             "👋 Панель керування Sense Nail Studio",
             reply_markup=get_client_reply_kb(),
         )
         await message.answer(
             ADMIN_WELCOME_TEXT,
             reply_markup=get_admin_main_kb(),
         )
     ```
   - Тепер для адміністратора ця ж кнопка знизу надійно повертає до панелі адміністратора.

---

### 3.2. Розширення моделі даних Appointment та безпечна міграція

1. **`src/database/models/appointment.py`:**
   - Додати нові колонки до моделі `Appointment`:
     ```python
     feedback_requested: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0", nullable=False)
     rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
     repeat_reminded: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0", nullable=False)
     ```

2. **`src/database/init_db.py`:**
   - Додати в блок безпечної автоматичної міграції для SQLite:
     ```python
     for col_def in [
         "reminded_24h INTEGER DEFAULT 0 NOT NULL",
         "reminded_2h INTEGER DEFAULT 0 NOT NULL",
         "admin_alerted INTEGER DEFAULT 0 NOT NULL",
         "feedback_requested INTEGER DEFAULT 0 NOT NULL",
         "rating INTEGER NULL",
         "repeat_reminded INTEGER DEFAULT 0 NOT NULL",
     ]:
         col_name = col_def.split()[0]
         try:
             await conn.execute(text(f"ALTER TABLE appointments ADD COLUMN {col_def}"))
             logger.info("Migrated appointments table: added column %s", col_name)
         except Exception:
             pass
     ```

---

### 3.3. Кнопка «📅 Додати в Google Календар»

1. **Генератор Google Calendar посилання (`src/bot.py`):**
   - Створити допоміжну функцію:
     ```python
     import urllib.parse
     from datetime import datetime, time, timedelta, timezone
     from zoneinfo import ZoneInfo

     KYIV_TZ = ZoneInfo("Europe/Kyiv")

     def generate_google_calendar_url(
         service_name: str,
         master_name: str,
         booking_date_val: date | str,
         start_time_val: time | str,
         end_time_val: time | str | None = None,
         salon_name: str = "Sense Nail Studio",
         address: str = "м. Івано-Франківськ, вул. Січових Стрільців",
     ) -> str:
         # Парсинг дати та часу
         if isinstance(booking_date_val, str):
             b_date = datetime.strptime(booking_date_val, "%Y-%m-%d").date() if "-" in booking_date_val else datetime.strptime(booking_date_val, "%d.%m.%Y").date()
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
     ```

2. **Оновлення `notify_client_booking_status` (`src/bot.py`):**
   - Додати параметр `end_time: str | None = None` у сигнатуру `notify_client_booking_status`.
   - При `status == "confirmed"`:
     - Згенерувати `gcal_url = generate_google_calendar_url(...)`.
     - Сформувати `reply_markup`:
       ```python
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
       ```
     - Відправити повідомлення з цією інлайн-кнопкою.

3. **Оновлення викликів `notify_client_booking_status`:**
   - У `src/api/routes/bookings.py` (ендпоінти `confirm` та `create_booking`): передавати `end_time=apt.end_time.strftime("%H:%M")`.
   - У `src/handlers/admin.py` (швидке підтвердження запису): передавати `end_time=apt.end_time.strftime("%H:%M")`.

---

### 3.4. NPS / Збір оцінки якості після візиту

1. **Фоновий процес опитування у `src/services/reminder_service.py`:**
   - Створити `process_feedback_requests(bot: Bot) -> None`:
     - Отримати поточний час у Києві: `now_kyiv = datetime.now(KYIV_TZ)`.
     - Запит:
       ```python
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
       ```
     - Для кожного запису:
       - `apt_end_dt = datetime.combine(apt.booking_date, apt.end_time, tzinfo=KYIV_TZ)`
       - `diff = now_kyiv - apt_end_dt`
       - Якщо `timedelta(hours=2) <= diff <= timedelta(hours=24)`:
         - Якщо у клієнта є коректний `telegram_id > 0`:
           - Текст:
             ```html
             💖 <b>Дякуємо, що завітали до Sense Nail Studio!</b>

             Ми прагнемо, щоб кожен візит дарував вам відчуття комфорту та бездоганний результат.
             Будь ласка, оцініть якість манікюру та обслуговування від 1 до 5 зірок:
             ```
           - Інлайн-клавіатура з 5 зірками:
             ```python
             InlineKeyboardMarkup(
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
             ```
           - Надіслати через `bot.send_message(..., parse_mode=ParseMode.HTML)`.
         - Встановити `apt.feedback_requested = True`.
       - Якщо `diff > timedelta(hours=24)` (застарілий запис):
         - Встановити `apt.feedback_requested = True` без надсилання, щоб не спамити за старі візити.
     - `await session.commit()`.

2. **Обробник оцінки в `src/handlers/client.py`:**
   - Зареєструвати обробник `callback_query(F.data.startswith("fb:"))`:
     ```python
     @client_router.callback_query(F.data.startswith("fb:"))
     async def client_feedback_callback(
         callback: CallbackQuery,
         session: AsyncSession,
         bot: Bot,
     ) -> None:
         # Парсимо apt_id та stars
         # Зберігаємо apt.rating = stars
         # Якщо stars >= 4:
         #   edit_text на "🌟 Щиро дякуємо за високу оцінку ({stars}/5)! 💖\n\nНам дуже приємно. Будемо раді бачити вас знову у Sense Nail Studio! ✨"
         # Якщо stars <= 3:
         #   edit_text на "Дякуємо за ваш відгук ({stars}/5). 🙏\nНам прикро, що щось пішло не так. Ми зв'яжемося з вами найближчим часом, щоб виправити ситуацію!"
         #   надіслати сповіщення адміністраторам settings.ADMIN_IDS про низьку оцінку з контактами клієнта
     ```

---

### 3.5. Автоматичне нагадування про повторний візит (21 день)

1. **Фоновий процес нагадування у `src/services/reminder_service.py`:**
   - Створити `process_repeat_visit_reminders(bot: Bot) -> None`:
     - Перевірити годину: надсилати виключно в денний проміжок `10:00 <= now_kyiv.hour < 19:00`. Якщо ні — виходити.
     - `today_kyiv = now_kyiv.date()`
     - Запит:
       ```python
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
       ```
     - Для кожного запису:
       - Якщо `apt.booking_date < today_kyiv - timedelta(days=35)`:
         # Запис надто старий (> 5 тижнів), спамити не потрібно
         `apt.repeat_reminded = True`
         `continue`
       - Перевірити, чи має клієнт вже майбутній запис (`booking_date >= today_kyiv` зі статусом `pending` або `confirmed`):
         ```python
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
         ```
       - Якщо майбутнього запису немає і `apt.client.telegram_id > 0`:
         - Текст:
           ```html
           💅 <b>Час оновити манікюр у Sense Nail Studio!</b> ✨

           {c_name}, минуло вже 3 тижні з вашого попереднього візиту.
           Для підтримки ідеальної форми та здоров'я нігтиків рекомендується оновлювати покриття кожні 3–4 тижні.

           Оберіть зручний час для наступного візиту у нашому онлайн-записі:
           ```
         - Інлайн-кнопки:
           `[ 💅 Записатися онлайн (Mini App) ]` (з WebApp URL)
           `[ 🏠 Головне меню ]`
         - Відправити клієнту повідомлення.
         - Встановити `apt.repeat_reminded = True`.
     - `await session.commit()`.

2. **Підключення до воркера:**
   - У `check_and_send_reminders(bot: Bot)` додати виклики:
     - `await process_feedback_requests(bot)`
     - `await process_repeat_visit_reminders(bot)`

---

### 3.6. Перезапуск демона та перевірка

1. Зупинити попередній процес:
   ```bash
   pkill -f "python -m src.main"
   ```
2. Запустити оновлений бекенд у фоні:
   ```bash
   nohup python -m src.main > app.log 2>&1 &
   ```
3. Перевірити, що процес запущений:
   ```bash
   pgrep -af "python -m src.main"
   ```
4. Перевірити останні логи `app.log` на відсутність помилок ініціалізації та успішну міграцію колонок.

---

## 4. Критерії приймання та валідація (Acceptance Criteria)
1. У Telegram боті відсутня стара кнопка «💅 Запис» у лівому нижньому куті (`MenuButtonWebApp` знято).
2. У нижній частині екрана по центру закріплена постійна зручна кнопка `[ 🏠 Головне меню ]` (`is_persistent=True`), яка коректно повертає користувача до головного меню (для клієнта — вітальне меню клієнта; для адміна — адмін-панель).
3. У моделі `Appointment` присутні нові поля: `feedback_requested`, `rating`, `repeat_reminded`, а автоматична SQLite міграція в `init_db.py` додає їх без втрати даних.
4. При підтвердженні запису надсилається інлайн-кнопка «📅 Додати в Google Календар» з точним посиланням на Google Календар.
5. Автономний воркер через 2 години після закінчення візиту надсилає 5 зірок для оцінки, обробляє колбек (подяка при 4-5 зірках, алерт адміну при 1-3 зірках).
6. Автономний воркер через 21 день пропонує клієнту оновити манікюр (якщо немає активного майбутнього запису).
7. Демон `python -m src.main` працює у фоновому режимі без помилок.
8. Усі зміни закомічені та відправлені на GitHub:
   ```bash
   git add .
   git commit -m "feat: replace webapp menu button with main menu reply keyboard and add marketing automation"
   git push origin main
   ```
