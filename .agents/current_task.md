# ТЕХНІЧНЕ ЗАВДАННЯ: Етап 1 — Базова архітектура Telegram-бота (aiogram 3.x), База даних та Рольова модель (RBAC)

## 1. Загальна інформація та конфігурація
- **Призначення:** Telegram-бот для манікюрного салону з чітким розподілом ролей (Адміністратор / Клієнт) та підготовкою структури під майбутній Telegram Mini App.
- **Bot Token:** `YOUR_BOT_TOKEN_HERE`
- **Admin TG ID:** `8607080614`
- **Admin Username:** `@andriy_bot_dev`
- **GitHub Repository:** `https://github.com/RissAR/nails_bot.git` (гілка `main`)
- **Стек:** Python 3.11+, aiogram 3.x, SQLAlchemy 2.0 (Async), aiosqlite (SQLite для локального старту з підтримкою зміни на PostgreSQL через DATABASE_URL), Pydantic Settings.

---

## 2. Обмеження та правила (Strict Scope Discipline)
1. **Zero Scope Creep:** Реалізувати **виключно** бекенд/бота, базу даних, конфігурацію та обробники ролей.
2. **Фронтенд Mini App поки НЕ створювати:** лише підготувати архітектуру під його інтеграцію.
3. **Безпека секретів:** Токен та ID адміністратора мають зчитуватися з `.env`. Створити `.env` з наданими даними та безпечний `.env.example`. Переконатися, що `.env` знаходиться в `.gitignore`.
4. **Git Автоматизація:** Після завершення розробки та перевірки обов'язково виконати `git add . && git commit -m "..." && git push -u origin main`.

---

## 3. Необхідна структура проекту
Рекомендується чиста модульна структура:
```text
LeadBot/
├── .agents/
│   ├── current_task.md
│   └── skills/
│       └── execute-task/
│           └── SKILL.md
├── src/
│   ├── __init__.py
│   ├── config.py             # Pydantic Settings (BOT_TOKEN, ADMIN_IDS, DB_URL)
│   ├── database/
│   │   ├── __init__.py
│   │   ├── session.py        # Async engine, sessionmaker, init_db()
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── base.py       # DeclarativeBase, timestamps
│   │       ├── user.py       # Модель User (ролі: CLIENT, ADMIN)
│   │       ├── service.py    # Модель Service (послуги манікюру)
│   │       ├── master.py     # Модель Master та зв'язок з послугами
│   │       └── appointment.py# Модель Appointment (записи)
│   ├── filters/
│   │   ├── __init__.py
│   │   └── admin.py          # IsAdminFilter
│   ├── middlewares/
│   │   ├── __init__.py
│   │   └── auth.py           # Auto-registration користувачів у БД при взаємодії
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── client.py         # /start для клієнта, інфо, контакти салону
│   │   ├── admin.py          # /start для адміна, /admin, меню керування
│   │   └── common.py         # Загальні команди /help, обробка помилок
│   ├── keyboards/
│   │   ├── __init__.py
│   │   ├── client_kb.py      # Клавіатури клієнта
│   │   └── admin_kb.py       # Клавіатури адміна
│   └── main.py               # Точка входу: запуск бота, диспетчера, ініціалізація БД
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 4. Конкретні вимоги до компонентів

### 4.1. Конфігурація (`src/config.py`)
- Завантаження з `.env`:
  - `BOT_TOKEN: str` (дефолт/змінна: `YOUR_BOT_TOKEN_HERE`)
  - `ADMIN_IDS: list[int]` (включає `8607080614`)
  - `DATABASE_URL: str` (за замовчуванням `sqlite+aiosqlite:///./nails_salon.db`)

### 4.2. База даних та Моделі (`src/database/`)
- Використовувати `SQLAlchemy 2.0` асинхронний синтаксис (`Mapped`, `mapped_column`).
- **User:**
  - `id: int` (PK)
  - `telegram_id: int` (BigInteger, unique, index=True)
  - `username: str | None`
  - `full_name: str`
  - `role: str` (`"client"` або `"admin"`, за замовчуванням `"client"`)
  - `phone: str | None`
  - `created_at: datetime`
- **Service:**
  - `id: int` (PK)
  - `name: str`
  - `description: str | None`
  - `duration_minutes: int` (тривалість процедури)
  - `price: float`
  - `is_active: bool` (default=True)
- **Master:**
  - `id: int` (PK)
  - `name: str`
  - `is_active: bool` (default=True)
- **Appointment:**
  - `id: int` (PK)
  - `client_id: int` (FK -> users.id)
  - `master_id: int` (FK -> masters.id)
  - `service_id: int` (FK -> services.id)
  - `booking_date: date`
  - `start_time: time`
  - `end_time: time`
  - `status: str` (`"pending"`, `"confirmed"`, `"rejected"`, `"cancelled"`)
  - `cancellation_reason: str | None`
  - `created_at: datetime`
- Функція `init_db()` для автоматичного створення таблиць при старті бота (без необхідності зовнішніх міграцій на першому етапі).

### 4.3. Авторизація та Мідлварі (`src/middlewares/auth.py`, `src/filters/admin.py`)
- **`AuthMiddleware`**:
  - При будь-якому повідомленні або callback від користувача перевіряє його наявність у БД.
  - Якщо користувача немає — автоматично створює запис.
  - Якщо `event.from_user.id in settings.ADMIN_IDS` — автоматично встановлює/підтверджує роль `"admin"`.
  - Передає об'єкт `db_user` у дані хендлера (`data["db_user"]`).
- **`IsAdminFilter`**:
  - Перевіряє, чи є користувач адміністратором (за `event.from_user.id in settings.ADMIN_IDS` або `db_user.role == 'admin'`).

### 4.4. Хендлери та Інтерфейс
- **Клієнтський режим (`src/handlers/client.py`):**
  - `/start`: Тепле привітання в манікюрному салоні, опис послуг, інлайн-кнопки (наприклад, "💅 Онлайн-запис (Скоро)", "ℹ️ Про салон", "📞 Контакти").
- **Адміністраторський режим (`src/handlers/admin.py`):**
  - Спрацьовує при `/start` від адміна або при команді `/admin`.
  - Вітальне повідомлення адміна: *"Вітаємо в панелі керування салоном!"*.
  - Інлайн-меню адміна:
    - 📋 Список послуг (перегляд існуючих послуг з БД або повідомлення про відсутність).
    - 📅 Графік майстрів (заглушка/попередній перегляд).
    - 🔔 Активні заявки (перегляд заявок зі статусом pending).

---

## 5. Валідація та Критерії готовності (Acceptance Criteria)
1. Створено віртуальне середовище / `requirements.txt` із зафіксованими версіями (`aiogram>=3.4.0`, `sqlalchemy>=2.0.0`, `aiosqlite`, `pydantic-settings`).
2. Код не містить синтаксичних помилок (перевірка через `python -m py_compile`).
3. Бот успішно запускається в режимі лонґ-полінгу (`polling`) і реагує на команди:
   - Від користувача 8607080614 відкривається адмінське меню.
   - Від стороннього користувача відкривається клієнтське меню.
4. База даних ініціалізується, користувач записується в таблицю `users`.
5. Зміни зафіксовані в git та відправлені на GitHub:
   ```bash
   git add .
   git commit -m "feat: initial bot structure with RBAC and database"
   git push -u origin main
   ```
