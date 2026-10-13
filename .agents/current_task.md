# ТЕХНІЧНЕ ЗАВДАННЯ: Етап 9 — Захист від подвійного бронювання (Race Condition Lock) та Автоматичні нагадування про візит

## 1. Загальна інформація та мета етапу
- **Мета:**
  1. **Race Condition Lock (Захист від подвійного бронювання):** Гарантувати, що двоє клієнтів не зможуть одночасно забронювати один і той самий таймслот у одного майстра. Якщо виникає конфлікт у мілісекундні інтервали — повертати HTTP 409 Conflict зі зрозумілим повідомленням та оновленням слотів у Mini App.
  2. **Автономний фоновий сервіс нагадувань (Background Reminder Worker):**
     - **Нагадування за 24 години до візиту:** надсилається клієнту в Telegram за день до запланованого часу.
     - **Нагадування за 2 години до візиту:** надсилається клієнту в день візиту за 2 години до початку.
     - **Автонагадування адміну про підвислі заявки:** якщо нова заявка висить у статусі `pending` понад 30 хвилин без підтвердження чи відхилення — надсилати адміну м'який пуш.
- **GitHub Repository:** `https://github.com/RissAR/nails_bot.git` (гілка `main`)
- **Стек:** Python (asyncio, SQLAlchemy 2.0 Async, zoneinfo), FastAPI, React, Telegram Bot API (aiogram 3.x).

---

## 2. Суворі правила безпеки (Strict Security & Scope Discipline)
1. **Zero Hardcoded Secrets (КРИТИЧНО):** `BOT_TOKEN` та інші конфіденційні дані зчитуються **виключно з локального `.env`**. Заборонено записувати токени у файли коду.
2. **Zero Scope Creep:** Модифікувати тільки роут створення бронювання (`src/api/routes/bookings.py`), модель `Appointment`, фоновий воркер нагадувань та обробку помилки 409 у `BookingModal.tsx`. Не ламати існуючий розклад чи дизайн.
3. **Git Автоматизація:** Після завершення роботи та перевірки виконати:
   `git add . && git commit -m "feat: implement race condition booking lock and background appointment reminders" && git push origin main`.

---

## 3. Деталі технічної реалізації

### 3.1. Захист від подвійного бронювання (Race Condition Lock)

#### Backend (`src/api/routes/bookings.py`):
1. **Транзакційна перевірка перетину інтервалів:**
   - Перед створенням запису `Appointment` виконати сувору перевірку наявності існуючих бронювань зі статусом `pending` або `confirmed` для того самого `master_id` та `booking_date`:
     ```python
     conflict_stmt = (
         select(Appointment)
         .where(
             Appointment.master_id == payload.master_id,
             Appointment.booking_date == b_date,
             Appointment.status.in_(["pending", "confirmed"]),
             Appointment.start_time < e_time,
             Appointment.end_time > s_time,
         )
     )
     ```
2. **In-Process Lock:**
   - Для запобігання паралельним конкурентним корутинам у FastAPI обгорнути створення запису в `asyncio.Lock()` (глобальний або по ключу `f"{payload.master_id}_{b_date}"`).
3. **Обробка колізії:**
   - Якщо знайдено перетин інтервалів:
     `raise HTTPException(status_code=409, detail="Цей часовий слот щойно забронював інший клієнт. Будь ласка, оберіть інший вільний час.")`.

#### Frontend (`frontend/src/components/BookingModal.tsx`):
- Перехоплювати помилку HTTP 409 під час виклику `api.createBooking()`:
  - Відображати зрозуміле повідомлення користувачу:
    *"⚠️ На жаль, цей час щойно зайняли. Будь ласка, оберіть інший вільний слот."*
  - Викликати зворотний колбек оновлення доступних слотів (`onRefreshSlots()`), щоб зайнятий слот миттєво зник з вибору.

---

### 3.2. Розширення моделі `Appointment` (`src/database/models/appointment.py`)
Додати прапорці відправки сповіщень для уникнення дублювання:
```python
reminded_24h: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0", nullable=False)
reminded_2h: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0", nullable=False)
admin_alerted: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0", nullable=False)
```
*(У `src/database/init_db.py` забезпечити додавання цих стовпців, якщо вони відсутні в існуючій базі даних через `ALTER TABLE` або перевірку).*

---

### 3.3. Сервіс автоматичних нагадувань (`src/services/reminder_service.py`)

Створити асинхронний фоновий воркер, що працює паралельно з ботом та API:
```python
async def run_reminder_worker(bot: Bot) -> None:
    """Background worker running every 60 seconds to process appointment reminders."""
```

#### Логіка перевірки за Київським часом (`Europe/Kyiv`):
1. **Нагадування за 24 години (Next-Day Reminder):**
   - Шукає `Appointment` зі статусом `"confirmed"` та `reminded_24h == False`.
   - Умова: `booking_date == tomorrow` (за часовим поясом Києва).
   - Надсилає клієнту в Telegram:
     ```html
     ✨ <b>Нагадування про завтрашній запис у Sense Nail Studio!</b>

     Олено, чекаємо на вас завтра (<b>{booking_date}</b>) о <b>{start_time}</b>:
     💅 <b>Послуга:</b> {service_name}
     👩‍🎨 <b>Майстер:</b> {master_name}
     📍 <b>Адреса:</b> м. Івано-Франківськ, вул. Січових Стрільців

     Якщо ваші плани змінилися, будь ласка, повідомте адміністратора: @andriy_bot_dev
     ```
   - Встановлює `reminded_24h = True` та зберігає в БД.

2. **Нагадування за 2 години (Same-Day Reminder):**
   - Шукає `Appointment` зі статусом `"confirmed"` та `reminded_2h == False`.
   - Умова: `booking_date == today` і поточний час знаходиться в діапазоні від 1.5 до 2.5 годин до `start_time`.
   - Надсилає клієнту в Telegram:
     ```html
     ⏳ <b>Чекаємо на вас сьогодні о {start_time}!</b>

     Студія естетичного манікюру «Sense Nail Studio».
     💅 {service_name} • Майстер: {master_name}
     📍 вул. Січових Стрільців

     Кава, чай та бездоганний манікюр уже чекають на вас ☕️✨
     ```
   - Встановлює `reminded_2h = True` та зберігає в БД.

3. **Автонагадування адміну про підвислі заявки (Pending Alert):**
   - Шукає `Appointment` зі статусом `"pending"` та `admin_alerted == False`.
   - Умова: запис створено понад 30 хвилин тому (`created_at <= now - 30 minutes`).
   - Надсилає адмінам (`settings.ADMIN_IDS`):
     ```html
     ⚠️ <b>Нагадування: Заявка #{id} все ще очікує рішення!</b>
     👤 Клієнт: {client_name} ({client_phone})
     💅 Послуга: {service_name} о {start_time} ({booking_date})
     Будь ласка, підтвердіть або відхиліть запис.
     ```
   - Встановлює `admin_alerted = True` та зберігає в БД.

---

### 3.4. Інтеграція в `src/main.py`
У головній асинхронній точці входу `main()`:
```python
await asyncio.gather(
    run_api(),
    run_bot(bot, dp),
    run_reminder_worker(bot),
)
```

---

## 4. Критерії приймання та валідація (Acceptance Criteria)
1. При спробі одночасного створення запису на пересічний час другий запит повертає HTTP 409 Conflict.
2. У Mini App користувач отримує попередження про зайнятий час та актуалізацію списку слотів.
3. У таблиці `appointments` додано поля `reminded_24h`, `reminded_2h`, `admin_alerted`.
4. Сервіс `run_reminder_worker` стартує в одному процесі, не блокує polling бота та API.
5. Повідомлення нагадувань надсилаються за часовим поясом `Europe/Kyiv` коректно і без дублювання.
6. `npm run build` у `frontend/` збирається без помилок (код 0).
7. Усі секрети залишаються строго в `.env`.
8. Зміни закомічені та відправлені на GitHub:
   ```bash
   git add .
   git commit -m "feat: implement race condition booking lock and background appointment reminders"
   git push origin main
   ```
