# Sense Nail Studio — Telegram Bot & Mini App 💅

Повнофункціональна екосистема (Telegram-бот + Telegram Mini App + REST API) для студії естетичного манікюру **«Sense Nail Studio»** (м. Івано-Франківськ).

Проект поєднує:
- 🤖 **Telegram-бот** на `aiogram 3.x` з рольовою моделлю доступу (RBAC), постійним нижнім меню, системою лояльності, NPS-опитуваннями та панеллю адміністратора.
- ⚡ **Захищений REST API** на `FastAPI` з криптографічною перевіркою `Telegram initData` (HMAC-SHA256), In-Memory Rate Limiting, захистом від подвійних бронювань (`asyncio.Lock`) та асинхронною ORM `SQLAlchemy 2.0`.
- 📱 **Telegram Mini App (TMA)** на `React 18`, `TypeScript`, `Vite` та `Tailwind CSS` в преміальному тактильному дизайні **«Silk & Caramel»** (Tactile Minimalist Luxury).
- 🐳 **DevOps & Надійність:** Багатоетапна Docker-контейнеризація (`Dockerfile` + `docker-compose.yaml`), автоматичні щоденні бекапи SQLite із ротацією 30 днів та моніторинг стану `/health`.

---

## 💎 Концепція студії Sense Nail Studio
- **Вайб бренду:** Затишна міська студія естетичного манікюру зі 100% стерильністю медичного рівня (сухожар, одноразові крафт-пакети).
- **Локація:** м. Івано-Франківськ, центр, вул. Січових Стрільців, 15.
- **Графік роботи:** Щодня з 09:00 до 20:00.

### Команда майстрів:
1. **Олена** (`Top Master`):
   - Досвід: 4 роки. Складні техніки, моделювання, френч, архітектура.
   - Графік: Пн, Ср, Пт, Нд (09:00 – 19:00).
2. **Вікторія** (`Master`):
   - Досвід: 2 роки. Апаратний/комбі-манікюр, нюд, японський еко-манікюр, SPA.
   - Графік: Вт, Чт, Сб (10:00 – 20:00).

---

## ✨ Ключовий функціонал

### Для клієнтів:
- **Онлайн-запис (Бот та Mini App):** вибір послуги за категоріями, перевірка сумісності майстра з послугою, інтерактивний 14-денний календар із розрахунком вільних слотів у реальному часі.
- **Програма лояльності:** прогресивна система знижок залежно від кількості завершених візитів:
  - `3+ візити` — **5%**
  - `5+ візитів` — **10%**
  - `10+ візитів` — **15%**
- **Google Calendar:** автоматичне генерація прямого посилання для додавання візиту в Google Calendar одразу після підтвердження майстром.
- **Розумні нагадування та Retention:**
  - Нагадування за **24 години** та за **2 години** до візиту.
  - Через **2 години після візиту** — автоматичне 5-зіркове опитування якості (NPS); при оцінці 5⭐ — пряме посилання на відгук у Google Maps.
  - Через **21 день після візиту** — персональне нагадування про корекцію покриття (якщо клієнт ще не записався повторно).

### Для адміністраторів:
- **Управління записами:** підтвердження в 1 клік, скасування або відхилення заявки із зазначенням причини (через пресети або власний текст у боті та Mini App).
- **Алерти непідтверджених заявок:** якщо заявка перебуває у статусі `pending` понад 15 хвилин, бот надсилає адміністраторам термінове нагадування.
- **CRUD послуг:** створення нових послуг, редагування назви, ціни та тривалості, м'яка деактивація послуг без втрати історії записів.
- **Керування графіком майстрів:** оперативне перемикання робочих/вихідних днів майстрів на найближчі 14 днів.

---

## 🛠 Технологічний стек
- **Backend & Bot:** Python 3.12, `aiogram 3.x`, `FastAPI`, `Uvicorn`, `SQLAlchemy 2.0 (Async)`, `aiosqlite`, `pydantic-settings`.
- **Frontend Mini App:** `React 18`, `TypeScript`, `Vite`, `Tailwind CSS`, `Lucide React`, Telegram WebApp API, шрифтова пара `Cormorant Garamond` + `Plus Jakarta Sans`.
- **Палітра дизайну «Silk & Caramel»:** Фон `#FAF6F0` (Warm Alabaster Silk), вторинний `#F2EAE0` (Soft Cashmere), акцент `#C89B7B` (Muted Caramel Bronze), текст `#38302B` (Deep Espresso).
- **Безпека та інфраструктура:** HMAC-SHA256 `X-Telegram-Init-Data` аутентифікація, `SlidingWindowRateLimiter`, CSP (`frame-ancestors` для Telegram), Docker multi-stage build, SQLite Online Backup API.

---

## 📁 Структура проекту
```text
LeadBot/
├── frontend/                        # React + TypeScript + Vite Telegram Mini App
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts            # HTTP-клієнт із передачею X-Telegram-Init-Data та cache-busting
│   │   ├── components/
│   │   │   ├── Header.tsx           # Шапка студії, бейдж лояльності, перемикач режиму адміна
│   │   │   ├── ServiceList.tsx      # Каталог послуг з категоріями та карткою лояльності
│   │   │   ├── MasterList.tsx       # Вибір майстра з перевіркою спеціалізації
│   │   │   ├── SlotPicker.tsx       # 14-денний календар та сітка доступних таймслотів
│   │   │   ├── BookingModal.tsx     # Модальне вікно запису з автозаповненням профілю та знижкою
│   │   │   └── AdminDashboard.tsx   # Адмін-панель (заявки, CRUD послуг, графік майстрів)
│   │   ├── types/
│   │   │   └── index.ts             # TypeScript-інтерфейси
│   │   ├── App.tsx                  # Головний компонент Mini App
│   │   ├── index.css                # Дизайн-система Silk & Caramel та анімації
│   │   └── main.tsx
│   ├── dist/                        # Зібраний production-бандл (роздається через FastAPI /app)
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── src/
│   ├── api/                         # Модуль FastAPI REST API
│   │   ├── app.py                   # Ініціалізація FastAPI, Security Headers, /health, роздача /app
│   │   ├── routes/
│   │   │   ├── auth.py              # GET /api/auth/me (профіль, роль, знижка лояльності)
│   │   │   ├── services.py          # GET/POST/PUT/PATCH /api/services (каталог та адмін CRUD)
│   │   │   ├── masters.py           # GET /api/masters, управління розкладом
│   │   │   ├── slots.py             # GET /api/slots (розрахунок вільних вікон)
│   │   │   └── bookings.py          # POST /api/bookings (з asyncio.Lock), адмін-операції та статистика
│   │   └── security/
│   │       ├── telegram_auth.py     # Валідація Telegram WebApp initData (HMAC-SHA256) та RBAC
│   │       └── rate_limiter.py      # SlidingWindowRateLimiter для захисту від спаму та DoS
│   ├── database/                    # Моделі SQLAlchemy 2.0, автоматичні міграції та сідінг
│   ├── handlers/                    # aiogram роутери (common, client, admin)
│   ├── keyboards/                   # Reply та Inline клавіатури з підтримкою WebAppInfo
│   ├── middlewares/                 # AuthMiddleware (RBAC для Telegram-бота)
│   ├── services/
│   │   ├── slot_calculator.py       # Алгоритм пошуку доступних таймслотів
│   │   ├── reminder_service.py      # Фоновий сервіс нагадувань, алертів, NPS та retention (21 день)
│   │   └── backup_service.py        # Щоденне резервне копіювання БД о 03:00 з ротацією 30 днів
│   ├── utils/
│   │   ├── validators.py            # Санітизація вводу та валідація телефонів (+380...)
│   │   ├── loyalty.py               # Розрахунок рівнів та знижок програми лояльності
│   │   └── calendar_link.py         # Генератор посилань Google Calendar
│   ├── config.py                    # Конфігурація через Pydantic Settings
│   └── main.py                      # Єдина точка входу: паралельний запуск FastAPI, бота та фонових воркерів
├── scripts/
│   └── backup.sh                    # Bash-скрипт для ручного/cron резервного копіювання SQLite
├── Dockerfile                       # Multi-stage Docker образ (Node 20 Alpine -> Python 3.12 Slim)
├── docker-compose.yaml              # Production оркестрація з volumes та healthcheck
├── .env.example                     # Шаблон змінних оточення
├── requirements.txt
└── README.md
```

---

## 🚀 Встановлення та запуск

### Варіант 1: Запуск через Docker Compose (Рекомендовано для Production)

1. Створіть файл `.env` на основі шаблону:
   ```bash
   cp .env.example .env
   ```
2. Заповніть `BOT_TOKEN`, `ADMIN_IDS` та `WEBAPP_URL` у файлі `.env`.
3. Запустіть контейнер:
   ```bash
   docker compose up -d --build
   ```
   База даних зберігається у `./data/nails_salon.db`, а щоденні резервні копії — у `./backups/`.

---

### Варіант 2: Локальний запуск (Для розробки)

#### 1. Налаштування віртуального середовища Python
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 2. Збірка фронтенду Mini App
```bash
cd frontend
npm install
npm run build
cd ..
```

#### 3. Налаштування змінних оточення
```bash
cp .env.example .env
```
Основні параметри в `.env`:
- `BOT_TOKEN` — токен вашого бота від `@BotFather`
- `ADMIN_IDS` — список Telegram ID адміністраторів у форматі JSON, напр. `[123456789]`
- `ADMIN_USERNAME` — контакт адміністратора (напр. `@your_admin_username`)
- `DATABASE_URL` — шлях до бази даних (`sqlite+aiosqlite:///./data/nails_salon.db`)
- `WEBAPP_URL` — публічний HTTPS URL до Mini App (наприклад, через Cloudflare Tunnel / Nginx)
- `API_PORT` — порт веб-сервера (за замовчуванням `8000`)
- `APP_VERSION` — версія бандлу для примусового скидання кешу Telegram WebView

#### 4. Запуск системи
```bash
python -m src.main
```
Сервер запуститься на `http://0.0.0.0:8000`:
- **Telegram Mini App:** `http://localhost:8000/app/`
- **Healthcheck:** `http://localhost:8000/health` (та `/api/health`)
- **Swagger API Docs:** `http://localhost:8000/docs`
- **Telegram Bot:** активний long-polling паралельно з фоновими сервісами нагадувань та бекапів.
