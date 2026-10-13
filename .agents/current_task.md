# ТЕХНІЧНЕ ЗАВДАННЯ: Етап 2 — Розробка Telegram Mini App (React + Tailwind) та зв'язка з Backend API

## 1. Загальна інформація та мета етапу
- **Мета:** Створити фронтенд Telegram Mini App (TMA) для клієнтів та адміністратора у затвердженому дизайні **«Warm Nude & Cashmere»** та підключити його до бекенду через REST API (FastAPI), що працює на тій самій базі даних і моделях.
- **Bot Token:** `YOUR_BOT_TOKEN_HERE`
- **Admin TG ID:** `8607080614`
- **Admin Username:** `@andriy_bot_dev`
- **Стек:**
  - **Frontend:** React 18+, Vite, TypeScript, Tailwind CSS, `@telegram-apps/sdk-react` (або `window.Telegram.WebApp`).
  - **Backend API:** FastAPI, Uvicorn, SQLAlchemy 2.0 (Async), aiosqlite (існуюча БД `nails_salon.db`).
  - **Telegram Bot:** aiogram 3.x (інтеграція кнопки відкриття Mini App у меню клієнта та адміна).

---

## 2. Суворі правила виконання (Strict Scope Discipline)
1. **Zero Scope Creep:** Робота стосується **виключно** створення фронтенду Mini App, API ендпоінтів та їх зв'язки. Поки НЕ налаштовуємо складне інтерактивне узгодження статусів (це буде наступний крок).
2. **Дизайн:** Суворо дотримуватися палітри **«Warm Nude & Cashmere»** (Фон `#FDFBF7`, акценти `#D4A373`, плашки `#FAEDCD`, текст `#2B2623`, білі картки з м'якими тінями `#FFFFFF`).
3. **Мобільна адаптивність:** Інтерфейс оптимізовано під екрани смартфонів всередині Telegram, з викликом `Telegram.WebApp.expand()` та Haptic Feedback при виборі слотів.
4. **Автономність:** Фронтенд збирається у `frontend/dist` та роздається через FastAPI як StaticFiles, забезпечуючи роботу системи на єдиному порту.
5. **Git Автоматизація:** Після завершення перевірки виконати:
   `git add . && git commit -m "feat: implement Telegram Mini App frontend with React, Tailwind, and FastAPI backend API" && git push origin main`.

---

## 3. Структура проекту після оновлення
```text
LeadBot/
├── frontend/                     # Новий React + Vite проект
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts         # Запити до /api (services, masters, slots, bookings)
│   │   ├── components/
│   │   │   ├── Header.tsx        # Інфо про салон Sense Nail Studio
│   │   │   ├── ServiceList.tsx   # Картки послуг за категоріями
│   │   │   ├── MasterList.tsx    # Вибір майстра (Олена, Вікторія)
│   │   │   ├── SlotPicker.tsx    # Календар і таймслоти
│   │   │   ├── BookingModal.tsx  # Підтвердження контактів і запис
│   │   │   └── AdminDashboard.tsx# Панель адміна (статистика, заявки, розклад)
│   │   ├── types/
│   │   │   └── index.ts          # Інтерфейси Service, Master, Slot, Appointment
│   │   ├── App.tsx               # Головний компонент (перемикання ролей клієнт/адмін)
│   │   ├── index.css             # Tailwind директиви та палітра Warm Nude
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── src/
│   ├── api/                      # Новий модуль REST API
│   │   ├── __init__.py
│   │   ├── app.py                # FastAPI додаток, CORS, роздача static frontend/dist
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── services.py       # GET /api/services
│   │       ├── masters.py        # GET /api/masters
│   │       ├── slots.py          # GET /api/slots
│   │       ├── bookings.py       # POST /api/bookings, GET /api/admin/bookings
│   │       └── auth.py           # GET /api/auth/me (валідація initData та роль)
│   ├── main.py                   # Оновлений запуск: паралельно FastAPI + aiogram polling
│   ├── config.py                 # Додано WEBAPP_URL, API_HOST, API_PORT
│   └── ... (існуючі модулі БД, моделей, хендлерів)
├── requirements.txt              # Додано fastapi>=0.110.0, uvicorn>=0.28.0
└── .agents/current_task.md
```

---

## 4. Специфікація Backend API (`src/api/`)

1. **`GET /api/services`**:
   - Повертає список категорій з активними послугами з БД (`id`, `name`, `duration_minutes`, `price`, `description`, `category_name`).
2. **`GET /api/masters`**:
   - Повертає список майстрів (`id`, `name`, `title`, `bio`, список `service_ids`, які виконує майстер).
3. **`GET /api/slots?master_id={id}&date={YYYY-MM-DD}&service_id={id}`**:
   - Розраховує вільні слоти на обрану дату для вказаного майстра з урахуванням:
     - робочих годин майстра на цей день (з таблиці `schedules`);
     - тривалості послуги + 15 хв буферного часу;
     - вже зайнятих слотів з таблиці `appointments` (`status in ['pending', 'confirmed']`).
   - Повертає масив часових рядків: `["10:00", "11:45", "14:00", "16:30"]`.
4. **`POST /api/bookings`**:
   - Приймає JSON:
     ```json
     {
       "service_id": 1,
       "master_id": 1,
       "booking_date": "2026-10-15",
       "start_time": "14:00",
       "client_name": "Олена",
       "client_phone": "+380970000000",
       "telegram_id": 123456789,
       "notes": "коментар"
     }
     ```
   - Створює запис `Appointment` зі статусом `"pending"`.
   - Повертає об'єкт створеного запису з `id` та `status`.
5. **`GET /api/admin/bookings`**:
   - Повертає список останніх заявок з деталями клієнта, послуги, майстра та статусу.
6. **`GET /api/admin/stats`**:
   - Повертає лічильники: кількість заявок `pending`, кількість підтверджених на сьогодні, загальну суму замовлень.
7. **`GET /api/auth/me`**:
   - Приймає заголовок або query-параметр `init_data` (або `tg_id` у режимі розробки).
   - Повертає `{ "telegram_id": ..., "role": "admin" | "client", "first_name": ... }`.

---

## 5. Специфікація Frontend Mini App (`frontend/`)

### 5.1. Дизайн та палітра Tailwind
У `tailwind.config.js` налаштувати кольори:
```javascript
colors: {
  nude: {
    bg: '#FDFBF7',
    surface: '#FFFFFF',
    primary: '#D4A373',
    primaryHover: '#C59261',
    accent: '#FAEDCD',
    secondary: '#F1EAE0',
    border: '#E8E2D8',
    text: '#2B2623',
    muted: '#7D7571',
    green: '#3E6B48',
    greenLight: '#E2EBE4',
  }
}
```

### 5.2. Функціональність Клієнтської частини:
- Вітальний блок «Sense Nail Studio» (Івано-Франківськ, вул. Січових Стрільців, 09:00–20:00).
- Крок 1: Таби категорій ("Всі", "Комплекси", "Нарощування", "Догляд") та вибір картки послуги (з динамічним підсвічуванням галочки).
- Крок 2: Вибір майстра — Олена (Top Master) або Вікторія (Master). Якщо послуга недоступна у майстра — картка блокується з відповідною підказкою.
- Крок 3: Горизонтальний календар на 14 днів вперед + динамічне завантаження вільних слотів з `/api/slots`.
- Закріплена нижня панель (Sticky Footer) з фінальною сумою, тривалістю та кнопкою «Записатися».
- Модальне вікно підтвердження: ім'я та телефон (автозаповнення з Telegram, якщо доступно), кнопка підтвердження відправки.
- Екран успіху: підтвердження прийняття заявки в обробку.

### 5.3. Функціональність Адміністраторської частини:
- Якщо користувач є адміністратором (`role === "admin"` або `telegram_id === 8607080614`), у шапці доступний перемикач `[ 💅 Клієнтська аппка | ⚙️ Панель адміна ]` (як у затвердженому макеті).
- Відображення карток метрик (Нові заявки, Сьогодні, Каса).
- Черга заявок у статусі `pending` з деталями клієнта та сумою.
- Огляд графіка майстрів на поточний день.

---

## 6. Інтеграція в Telegram Bot (`src/`)

- В `src/config.py`:
  - `WEBAPP_URL: str = "http://localhost:8000/app"` (або конфігурований URL з `.env`).
  - `API_HOST: str = "0.0.0.0"`
  - `API_PORT: int = 8000`
- В `src/keyboards/client_kb.py`:
  - Кнопка "💅 Онлайн-запис" тепер має тип `web_app=WebAppInfo(url=settings.WEBAPP_URL)`.
- В `src/keyboards/admin_kb.py`:
  - Додати кнопку "📱 Відкрити адмін-панель TMA" з `web_app=WebAppInfo(url=settings.WEBAPP_URL)`.
- В `src/main.py`:
  - Запуск uvicorn сервера з FastAPI одночасно з лонґ-полінгом бота за допомогою `asyncio.gather()`.

---

## 7. Критерії приймання та валідація (Acceptance Criteria)
1. Фронтенд успішно компілюється: `npm run build` у директорії `frontend/` завершується з кодом 0, згенеровано файли у `frontend/dist`.
2. Бекенд API успішно піднімається на порті 8000 і віддає дані:
   - `GET http://localhost:8000/api/services` повертає JSON з 9 послугами;
   - `GET http://localhost:8000/api/masters` повертає Олену та Вікторію;
   - `GET http://localhost:8000/app/` віддає зібраний клієнтський SPA Mini App.
3. У боті кнопки «Онлайн-запис» та «Адмін-панель TMA» відкривають WebApp.
4. Всі зміни закомічені та відправлені на GitHub:
   ```bash
   git add .
   git commit -m "feat: implement Telegram Mini App frontend with React, Tailwind, and FastAPI backend API"
   git push origin main
   ```
