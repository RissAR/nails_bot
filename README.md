# Sense Nail Studio — Telegram Bot & Mini App 💅

Повнофункціональний Telegram-бот та Telegram Mini App (TMA) для студії естетичного манікюру **«Sense Nail Studio»** (м. Івано-Франківськ).

Проект поєднує:
- 🤖 **Telegram-бот** на `aiogram 3.x` з рольовою моделлю доступу (RBAC) та кнопками WebApp.
- ⚡ **REST API** на `FastAPI`, що працює асинхронно з базою даних SQLAlchemy 2.0.
- 📱 **Telegram Mini App** на `React 18`, `TypeScript`, `Vite` та `Tailwind CSS` в естетичному дизайні **«Warm Nude & Cashmere»**.

---

## 💎 Концепція студії Sense Nail Studio
- **Вайб бренду:** Затишна міська студія естетичного манікюру зі 100% стерильністю медичного рівня (сухожар, одноразові крафт-пакети).
- **Локація:** м. Івано-Франківськ, центр, вул. Січових Стрільців.
- **Графік роботи:** Щодня з 09:00 до 20:00.

### Команда майстрів:
1. **Олена** (`Top Master`):
   - Досвід: 4 роки. Складні техніки, моделювання, френч, архітектура.
   - Графік: Пн, Ср, Пт, Нд (09:00 – 19:00).
2. **Вікторія** (`Master`):
   - Досвід: 2 роки. Апаратний/комбі-манікюр, нюд, японський еко-манікюр, SPA.
   - Графік: Вт, Чт, Сб (10:00 – 20:00).

---

## 🛠 Технологічний стек
- **Backend & Bot:** Python 3.11+, `aiogram 3.x`, `FastAPI`, `Uvicorn`, `SQLAlchemy 2.0 (Async)`, `aiosqlite`, `pydantic-settings`.
- **Frontend Mini App:** `React 18`, `TypeScript`, `Vite`, `Tailwind CSS`, `Lucide React`, Telegram WebApp API.
- **Палітра дизайну:** Warm Nude & Cashmere (Фон `#FDFBF7`, акцент `#D4A373`, поверхня `#FFFFFF`, текст `#2B2623`).

---

## 📁 Структура проекту
```text
LeadBot/
├── frontend/                     # React + Vite Telegram Mini App
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts         # Запити до REST API
│   │   ├── components/
│   │   │   ├── Header.tsx        # Шапка студії та перемикач ролей адміна
│   │   │   ├── ServiceList.tsx   # Каталог послуг з фільтрацією за табами
│   │   │   ├── MasterList.tsx    # Вибір майстра та перевірка сумісності
│   │   │   ├── SlotPicker.tsx    # 14-денний календар та динамічні таймслоти
│   │   │   ├── BookingModal.tsx  # Модальне вікно запису та підтвердження
│   │   │   └── AdminDashboard.tsx# Панель адміна (метрики, черга заявок)
│   │   ├── types/
│   │   │   └── index.ts          # Інтерфейси Service, Master, Booking тощо
│   │   ├── App.tsx               # Головний компонент Mini App
│   │   ├── index.css             # Tailwind директиви
│   │   └── main.tsx
│   ├── dist/                     # Зібраний production-бандл (роздається FastAPI)
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── src/
│   ├── api/                      # Модуль FastAPI REST API
│   │   ├── app.py                # Створення додатку, CORS, роздача static /app
│   │   └── routes/
│   │       ├── services.py       # GET /api/services
│   │       ├── masters.py        # GET /api/masters
│   │       ├── slots.py          # GET /api/slots
│   │       ├── bookings.py       # POST /api/bookings, GET /api/admin/bookings, stats
│   │       └── auth.py           # GET /api/auth/me
│   ├── config.py                 # Pydantic Settings
│   ├── database/                 # База даних, моделі та сідінг
│   ├── handlers/                 # aiogram хендлери
│   ├── keyboards/                # Клавіатури з WebAppInfo
│   ├── middlewares/              # AuthMiddleware (RBAC)
│   └── main.py                   # Одночасний запуск FastAPI та aiogram через asyncio.gather()
├── .env                          # Локальні змінні оточення
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🚀 Встановлення та запуск

### 1. Клонування репозиторію
```bash
git clone https://github.com/RissAR/nails_bot.git
cd nails_bot
```

### 2. Налаштування віртуального середовища Python
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Збірка фронтенду Mini App
```bash
cd frontend
npm install
npm run build
cd ..
```

### 4. Змінні оточення
```bash
cp .env.example .env
```
Параметри в `.env`:
- `BOT_TOKEN`: токен бота від BotFather
- `ADMIN_IDS`: `[8607080614]`
- `WEBAPP_URL`: URL до Mini App (за замовчуванням `http://localhost:8000/app` або ngrok URL для мобільного тестування в Telegram)
- `API_PORT`: `8000`

### 5. Запуск системи (Бот + FastAPI)
```bash
python -m src.main
```
Сервер підніметься на `http://0.0.0.0:8000`:
- **Mini App:** `http://localhost:8000/app/`
- **Swagger Docs:** `http://localhost:8000/docs`
- **Telegram Bot:** активний polling у Telegram.
