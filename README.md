# Nails Salon Telegram Bot 💅

Telegram-бот для манікюрного салону з рольовою моделлю доступу (RBAC: Адміністратор / Клієнт) та модульною асинхронною архітектурою, підготовленою під інтеграцію з Telegram Mini App.

## 🛠 Технологічний стек
- **Python:** 3.11+
- **Фреймворк бота:** [aiogram 3.x](https://docs.aiogram.dev/)
- **ORM / База даних:** [SQLAlchemy 2.0 (Async)](https://docs.sqlalchemy.org/) + `aiosqlite` (SQLite за замовчуванням, підтримка PostgreSQL через `DATABASE_URL`)
- **Конфігурація:** [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

---

## 📁 Структура проекту
```text
LeadBot/
├── .agents/                  # Інструкції та навички агентів
│   ├── current_task.md
│   └── skills/
├── src/
│   ├── __init__.py
│   ├── config.py             # Налаштування зчитування .env
│   ├── database/
│   │   ├── __init__.py
│   │   ├── session.py        # Асинхронний engine, sessionmaker, init_db()
│   │   └── models/           # SQLAlchemy 2.0 моделі
│   │       ├── __init__.py
│   │       ├── base.py       # DeclarativeBase, TimestampMixin
│   │       ├── user.py       # User (ролі: client, admin)
│   │       ├── service.py    # Service (послуги манікюру)
│   │       ├── master.py     # Master (майстри салону)
│   │       └── appointment.py# Appointment (записи на процедури)
│   ├── filters/
│   │   ├── __init__.py
│   │   └── admin.py          # IsAdminFilter (перевірка ролі адміна)
│   ├── middlewares/
│   │   ├── __init__.py
│   │   └── auth.py           # Авто-реєстрація та призначення ролей у БД
│   ├── keyboards/
│   │   ├── __init__.py
│   │   ├── client_kb.py      # Інлайн-клавіатури для клієнтів
│   │   └── admin_kb.py       # Інлайн-клавіатури для адмін-панелі
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── client.py         # Клієнтські хендлери (/start, інфо, контакти)
│   │   ├── admin.py          # Адмінські хендлери (/start, /admin, послуги, заявки)
│   │   └── common.py         # Загальні хендлери (/help)
│   └── main.py               # Точка входу: ініціалізація та polling
├── .env                      # Локальні змінні оточення (ігнорується git)
├── .env.example              # Приклад файлу налаштувань
├── .gitignore                # Фільтрація артефактів та секретів
├── requirements.txt          # Фіксовані залежності проекту
└── README.md                 # Документація проекту
```

---

## 🚀 Встановлення та запуск

### 1. Клонування репозиторію
```bash
git clone https://github.com/RissAR/nails_bot.git
cd nails_bot
```

### 2. Створення та активація віртуального середовища
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux / macOS
# або .venv\Scripts\activate для Windows
```

### 3. Встановлення залежностей
```bash
pip install -r requirements.txt
```

### 4. Налаштування змінних оточення
Створіть `.env` на основі `.env.example`:
```bash
cp .env.example .env
```
Відредагуйте параметри за необхідності:
- `BOT_TOKEN` — токен бота від BotFather
- `ADMIN_IDS` — список Telegram ID адміністраторів (наприклад, `[8607080614]`)
- `DATABASE_URL` — посилання на базу даних (за замовчуванням `sqlite+aiosqlite:///./nails_salon.db`)

### 5. Запуск бота
```bash
python -m src.main
```

---

## 👥 Рольова модель (RBAC)
- **Клієнт:** При надсиланні `/start` користувач автоматично реєструється в базі даних з роллю `client`. Клієнт отримує доступ до інформації про салон, контакти та анонс онлайн-запису через Mini App.
- **Адміністратор:** Якщо Telegram ID користувача є у списку `ADMIN_IDS`, йому автоматично призначається роль `admin`. Адміністратор отримує вітання адмін-панелі та доступ до команд `/start` і `/admin`, перегляду послуг салону, графіку майстрів та активних заявок зі статусом `pending`.
