# Sense Nail Studio — Telegram Bot 💅

Telegram-бот для студії естетичного манікюру **«Sense Nail Studio»** (м. Івано-Франківськ) з повною рольовою моделлю доступу (RBAC: Клієнт / Адміністратор), модульною архітектурою на базі `aiogram 3.x`, базою даних SQLAlchemy 2.0 (Async) та сідінгом бізнес-концепції студії.

---

## 💎 Концепція студії Sense Nail Studio
- **Вайб бренду:** Затишна міська студія естетичного манікюру, де турбота про здоров'я нігтів поєднується зі 100% стерильністю медичного рівня (сухожар, одноразові крафт-пакети) та сучасним сервісом.
- **Локація:** м. Івано-Франківськ, центр, вул. Січових Стрільців.
- **Графік роботи:** Щодня з 09:00 до 20:00.

### Команда майстрів:
1. **Олена** (`Top Master`):
   - Досвід: 4 роки.
   - Спеціалізація: Складні техніки, моделювання нігтів, френч, ремонт та відновлення архітектури.
   - Графік: Пн, Ср, Пт, Нд (09:00 – 19:00).
2. **Вікторія** (`Master`):
   - Досвід: 2 роки.
   - Спеціалізація: Апаратний та комбі-манікюр, нюдові покриття, японський еко-манікюр, SPA-догляд.
   - Графік: Вт, Чт, Сб (10:00 – 20:00).

### Каталог послуг:
- **Комплекси манікюру:**
  - `Комплекс «Базовий Однотон»`: 90 хв (1.5 год), 550 грн (Олена, Вікторія)
  - `Комплекс «Френч / Градієнт»`: 105 хв (1 год 45 хв), 650 грн (Олена, Вікторія)
  - `Гігієнічний манікюр`: 45 хв, 350 грн (Олена, Вікторія)
  - `Японський Еко-манікюр`: 60 хв, 450 грн (лише Вікторія)
- **Моделювання та нарощування:**
  - `Нарощування нігтів (з нуля)`: 150 хв (2.5 год), 900 грн (лише Олена)
  - `Корекція нарощених нігтів`: 120 хв (2 год), 750 грн (лише Олена)
- **Доглядові послуги та Add-ons:**
  - `Ремонт / Донарощування 1 нігтя`: 15 хв, 70 грн (Олена, Вікторія)
  - `Укріплення гелем / акрилом`: 20 хв, 150 грн (Олена, Вікторія)
  - `SPA-догляд (Парафінотерапія)`: 30 хв, 200 грн (Олена, Вікторія)

---

## 🛠 Технологічний стек
- **Python:** 3.11+
- **Telegram Bot Framework:** [aiogram 3.x](https://docs.aiogram.dev/)
- **ORM / База даних:** [SQLAlchemy 2.0 (Async)](https://docs.sqlalchemy.org/) + `aiosqlite` (SQLite локально з можливістю підключення PostgreSQL через `DATABASE_URL`)
- **Конфігурація:** [pydantic-settings](https://docs.pydantic.dev/)

---

## 📁 Структура проекту
```text
LeadBot/
├── .agents/
│   ├── current_task.md
│   └── skills/
│       └── execute-task/
│           └── SKILL.md
├── src/
│   ├── __init__.py
│   ├── config.py              # Pydantic Settings (BOT_TOKEN, ADMIN_IDS, DB_URL, SALON_NAME)
│   ├── database/
│   │   ├── __init__.py
│   │   ├── session.py         # Async engine, sessionmaker, get_session()
│   │   ├── init_db.py         # Створення таблиць + функція seed_initial_data()
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── base.py        # DeclarativeBase, TimestampMixin
│   │       ├── user.py        # User (telegram_id, username, full_name, role)
│   │       ├── category.py    # Category (id, name, slug)
│   │       ├── service.py     # Service (category_id, name, description, duration_minutes, price, is_active)
│   │       ├── master.py      # Master (name, title, bio, is_active) та MasterService
│   │       ├── schedule.py    # Schedule (master_id, day_of_week, start_time, end_time, is_day_off)
│   │       └── appointment.py # Appointment (client_id, master_id, service_id, date, start_time, end_time, status)
│   ├── filters/
│   │   ├── __init__.py
│   │   └── admin.py           # IsAdminFilter
│   ├── middlewares/
│   │   ├── __init__.py
│   │   └── auth.py            # AuthMiddleware: реєстрація у БД, присвоєння ролі admin для 8607080614
│   ├── keyboards/
│   │   ├── __init__.py
│   │   ├── client_kb.py       # Inline-клавіатури клієнта (Каталог, Майстри, Контакти, Запис)
│   │   └── admin_kb.py        # Панель керування адміна (Послуги, Майстри, Заявки, Статистика)
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── client.py          # /start (для клієнта), перегляд каталогу з БД, майстрів, контактів
│   │   ├── admin.py           # /start (для адміна), /admin, навігація по адмін-панелі
│   │   └── common.py          # /help, обробка невідомих команд
│   └── main.py                # Запуск бота (aiogram 3.x polling), підключення мідлварей та роутерів
├── .env                       # Змінні оточення (ігнорується git)
├── .env.example               # Приклад налаштувань
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Встановлення та запуск

1. **Клонування та перехід у директорію:**
   ```bash
   git clone https://github.com/RissAR/nails_bot.git
   cd nails_bot
   ```

2. **Створення віртуального середовища:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Встановлення залежностей:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Налаштування `.env`:**
   ```bash
   cp .env.example .env
   ```

5. **Запуск бота:**
   ```bash
   python -m src.main
   ```
   При першому запуску база даних створюється автоматично та наповнюється сід-даними (3 категорії, 9 послуг, 2 майстри з розкладом). Повторні запуски не дублюють дані.
