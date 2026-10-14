# ТЕХНІЧНЕ ЗАВДАННЯ: Етап 12 — Безпека API (Блок 4) та Контейнеризація Docker Compose (Блок 2)

## 1. Загальна інформація та мета етапу
- **Мета:**
  1. **Безпека та фіналізація API (Блок 4):**
     - **Криптографічна верифікація Telegram initData:** реалізувати валідацію HMAC-SHA256 підпису з перевіркою терміну дії `auth_date` (захист від підробки та replay-атак).
     - **Адміністративна авторизація:** захистити всі ендпоінти `/api/admin/*` (`/bookings`, `/confirm`, `/reject`, `/stats`) за допомогою FastAPI dependency `verify_admin_access`. Запити від неавторизованих користувачів блокувати з `HTTP 403 Forbidden`.
     - **Оновлення клієнта Mini App (`frontend/src/api/client.ts`):** автоматично надсилати заголовок `X-Telegram-Init-Data` у запитах до API.
     - **Rate Limiting (Захист від спаму/DoS):** впровадити in-memory Sliding Window Rate Limiter (ліміт 5 запитів/хв для `POST /api/bookings`, 60 запитів/хв для `GET /api/slots`). Перевищення повертає `HTTP 429 Too Many Requests`.
     - **Healthcheck ендпоінти (`GET /health` та `GET /api/health`):** перевірка статусу сервісу та з'єднання з базою даних (`SELECT 1`) для Docker-моніторингу.
     - **Security Headers Middleware:** додати обов'язкові безпекові HTTP-заголовки (`X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `Referrer-Policy`).
  2. **Контейнеризація та підготовка до деплою на Ubuntu Server (Блок 2):**
     - **Багатоетапний `Dockerfile`:** Stage 1 — збірка фронтенду через `node:20-alpine`; Stage 2 — `python:3.12-slim` із запуском бота, API та воркерів.
     - **`docker-compose.yaml`:** сервіс `app` із директивою `restart: always`, прокиданням порту `8000:8000`, монтуванням volume для бази даних `./data:/app/data` та бекапів `./backups:/app/backups`, завантаженням `.env` та вбудованим `healthcheck`.
     - **`.dockerignore`:** виключення локальних файлів (`node_modules`, `.git`, `.env`, логів, баз даних) з контексту збірки.
     - **Автономний щоденний бекап бази даних:**
       - Внутрішній фоновий сервіс (`src/services/backup_service.py`): щоночі о 03:00 (Kyiv TZ) робить снепшот SQLite через `VACUUM INTO` у папку `backups/` з ротацією (видалення бекапів старших за 30 днів).
       - Зовнішній bash-скрипт (`scripts/backup.sh`): для ручного запуску або crontab хост-системи.
     - **Підтримка директорії `data/`:** автоматичне створення папки при старті в `src/database/session.py` та міграція існуючого файлу `nails_salon.db` в `./data/nails_salon.db` без втрати записів.
- **GitHub Repository:** `https://github.com/RissAR/nails_bot.git` (гілка `main`)
- **Стек:** FastAPI, Python 3.12, Docker, Docker Compose, Node.js 20, Vite, React, SQLite, aiogram 3.x.

---

## 2. Суворі правила безпеки та дисципліни (Strict Scope Discipline)
1. **Zero Hardcoded Secrets (КРИТИЧНО):** `BOT_TOKEN`, `ADMIN_IDS` та інші налаштування зчитуються **виключно з `.env`**. Заборонено прописувати секрети у файлах коду або `docker-compose.yaml`.
2. **Zero Scope Creep:** Робота ведеться виключно над API-ендпоінтами, безпекою, заголовками, контейнеризацією та бекапами. Не змінювати робочу UI-логіку чи поведінку телеграм-бота.
3. **Збереження даних:** Не видаляти діючу базу `nails_salon.db`. Якщо база знаходиться в корені — автоматично забезпечити її перенесення/копіювання в `./data/nails_salon.db`.
4. **Git Автоматизація:** Після успішного тестування виконати:
   `git add . && git commit -m "feat: implement API security, rate limiting, docker-compose and automated backup" && git push origin main`.

---

## 3. Деталі технічної реалізації

### 3.1. БЛОК 4: Безпека API та авторизація

#### 1. Модуль криптографічної перевірки Telegram initData (`src/api/security/telegram_auth.py`):
Створити файл `src/api/security/telegram_auth.py` з функціями:
- `validate_telegram_init_data(init_data_raw: str, bot_token: str) -> dict | None`:
  1. Розпарсити `init_data_raw` на параметри через `urllib.parse.parse_qsl`.
  2. Знайти та вилучити параметр `hash`.
  3. Відсортувати залишок пар за ключем за алфавітом.
  4. Сформувати рядок `data_check_string = "\n".join(f"{k}={v}" for k, v in sorted_items)`.
  5. Обчислити `secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()`.
  6. Обчислити `calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()`.
  7. Порівняти `calculated_hash` та `hash` через `hmac.compare_digest`.
  8. Перевірити `auth_date`: якщо `abs(time.time() - int(auth_date)) > 86400`, вважати недійсним.
  9. Розпарсити `user` JSON у словник з полями `id`, `first_name`, `username`.
- FastAPI Dependency `get_current_telegram_user(request: Request, x_telegram_init_data: str | None = Header(None, alias="X-Telegram-Init-Data"), init_data: str | None = Query(None), tg_id: int | None = Query(None)) -> dict`:
  - Якщо передано `init_data` (з заголовка або query): валідувати через `validate_telegram_init_data`.
  - Якщо підпис коректний — повернути дані користувача (`telegram_id`, `role`).
  - Якщо передано лише `tg_id` (для локального тестування при відсутності `initData`): дозволяти, якщо `BOT_TOKEN` не налаштовано або `tg_id in settings.ADMIN_IDS`.
  - Інакше — повертати гостьовий контекст.
- FastAPI Dependency `verify_admin_access(user: dict = Depends(get_current_telegram_user)) -> dict`:
  - Перевірити: `user.get("telegram_id") in settings.ADMIN_IDS`.
  - Якщо ні — підняти `HTTPException(status_code=403, detail="Доступ заборонено: потрібні права адміністратора.")`.

#### 2. Захист адміністративних ендпоінтів у `src/api/routes/bookings.py`:
- Додати `dependencies=[Depends(verify_admin_access)]` або аргумент `admin_user: dict = Depends(verify_admin_access)` до ендпоінтів:
  - `GET /admin/bookings`
  - `PATCH /admin/bookings/{booking_id}/confirm`
  - `PATCH /admin/bookings/{booking_id}/reject`
  - `GET /admin/stats`
- Тепер сторонній клієнт без валідного `initData` адміністратора не зможе переглядати конфіденційні номери телефонів чи змінювати статус записів.

#### 3. Інтеграція `X-Telegram-Init-Data` у Frontend (`frontend/src/api/client.ts`):
- Створити хелпер `getHeaders()`:
  ```typescript
  function getHeaders(contentType: boolean = false): Record<string, string> {
    const headers: Record<string, string> = {};
    if (contentType) headers['Content-Type'] = 'application/json';
    const initData = window.Telegram?.WebApp?.initData;
    if (initData) {
      headers['X-Telegram-Init-Data'] = initData;
    }
    return headers;
  }
  ```
- Застосувати `getHeaders()` до всіх викликів `fetch` (`getAdminBookings`, `confirmBooking`, `rejectBooking`, `getAdminStats`, `createBooking`, `getAuthMe`).

#### 4. Rate Limiting (`src/api/security/rate_limiter.py`):
Створити клас `SlidingWindowRateLimiter`:
- Зберігає часові мітки запитів для кожного IP-адреси / `telegram_id` в пам'яті (`defaultdict(list)`).
- Періодично очищає застарілі записи (> 60 сек).
- Методи перевірки для використання як Dependency:
  - `rate_limit_bookings`: максимум 5 запитів за 60 секунд на IP / клієнта.
  - `rate_limit_slots`: максимум 60 запитів за 60 секунд на IP.
- При перевищенні ліміту піднімати `HTTPException(status_code=429, detail="Забагато запитів. Будь ласка, зачекайте хвилину перед повторною спробою.")`.
- Підключити `rate_limit_bookings` до `POST /api/bookings`, а `rate_limit_slots` до `GET /api/slots`.

#### 5. Healthcheck ендпоінти (`src/api/app.py`):
- Додати маршрути `GET /health` та `GET /api/health`:
  ```python
  @app.get("/health", tags=["Health"])
  @app.get("/api/health", tags=["Health"])
  async def healthcheck():
      db_status = "connected"
      try:
          async with async_session_maker() as session:
              await session.execute(text("SELECT 1"))
      except Exception as e:
          db_status = f"error: {str(e)}"
          return JSONResponse(
              status_code=503,
              content={"status": "unhealthy", "database": db_status, "version": settings.APP_VERSION},
          )
      return {
          "status": "healthy",
          "database": db_status,
          "salon": settings.SALON_NAME,
          "version": settings.APP_VERSION,
      }
  ```

#### 6. Security Headers Middleware (`src/api/app.py`):
- Додати мідлвар для встановлення HTTP Security Headers:
  ```python
  @app.middleware("http")
  async def add_security_headers(request: Request, call_next):
      response = await call_next(request)
      response.headers["X-Content-Type-Options"] = "nosniff"
      response.headers["X-Frame-Options"] = "SAMEORIGIN"
      response.headers["X-XSS-Protection"] = "1; mode=block"
      response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
      return response
  ```

---

### 3.2. БЛОК 2: Контейнеризація та Інфраструктура (Ubuntu Server)

#### 1. Оптимізований багатоетапний `Dockerfile`:
Створити у корені проекту `Dockerfile`:
```dockerfile
# Stage 1: Build Telegram Mini App (Frontend)
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Production Runtime (Python + SQLite)
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Create persistent storage directories
RUN mkdir -p /app/data /app/backups

# Copy application source code
COPY src/ ./src/
COPY scripts/ ./scripts/
RUN chmod +x ./scripts/*.sh 2>/dev/null || true

# Copy built frontend assets from Stage 1
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "src.main"]
```

#### 2. Файл `docker-compose.yaml`:
Створити у корені проекту `docker-compose.yaml`:
```yaml
version: '3.8'

services:
  sense_bot:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: sense_nail_bot
    restart: always
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./backups:/app/backups
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 15s
    logging:
      driver: "json-file"
      options:
        max-size: "20m"
        max-file: "5"
```

#### 3. Файл `.dockerignore`:
Створити у корені проекту `.dockerignore`:
```text
.git
.github
.agents
.env
*.log
__pycache__
*.pyc
*.pyo
*.pyd
.pytest_cache
node_modules
frontend/node_modules
data/*.db
backups/*.db
nails_salon.db
app.log
cloudflared.log
```

#### 4. Автоматичний щоденний бекап бази даних:
- **Внутрішній автономний воркер (`src/services/backup_service.py`):**
  - Функція `run_backup_worker()`:
    - Працює у нескінченному циклі з перевіркою щогодини.
    - О 03:00 ночі (Kyiv TZ) виконує безпечний бекап поточної SQLite бази даних.
    - Шлях збереження: `backups/nails_salon_YYYYMMDD_030000.db`.
    - Для створення бекапу викликати SQLite команду `VACUUM INTO '<шлях>'` через `session.execute(text(...))` або `sqlite3.connect().backup()`. Це гарантує 100% консистентність без блокування читання/запису.
    - Ротація: перевіряє папку `backups/` та видаляє файли старші за 30 днів.
    - Логує результат створення та очищення.
  - Додати `run_backup_worker()` в `asyncio.gather(...)` у `src/main.py`.
- **Зовнішній bash-скрипт (`scripts/backup.sh`):**
  - Створити `scripts/backup.sh`:
    ```bash
    #!/usr/bin/env bash
    set -euo pipefail

    BACKUP_DIR="${BACKUP_DIR:-./backups}"
    DB_PATH="${DB_PATH:-./data/nails_salon.db}"
    mkdir -p "$BACKUP_DIR"

    if [ ! -f "$DB_PATH" ]; then
      if [ -f "./nails_salon.db" ]; then
        DB_PATH="./nails_salon.db"
      else
        echo "Database file not found at $DB_PATH or ./nails_salon.db"
        exit 1
      fi
    fi

    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    BACKUP_FILE="$BACKUP_DIR/nails_salon_${TIMESTAMP}.db"

    sqlite3 "$DB_PATH" ".backup '$BACKUP_FILE'"
    echo "Backup created successfully: $BACKUP_FILE"

    # Ротація (видалення бекапів старших за 30 днів)
    find "$BACKUP_DIR" -type f -name "nails_salon_*.db" -mtime +30 -delete
    echo "Old backups (>30 days) cleaned up."
    ```
  - Надати права: `chmod +x scripts/backup.sh`.

#### 5. Адаптація шляхів бази даних (`src/database/session.py` та `src/config.py`):
- У `src/config.py`:
  - Встановити `DATABASE_URL: str = "sqlite+aiosqlite:///./data/nails_salon.db"`.
- У `src/database/session.py` (перед створенням engine або при старті):
  - Якщо вказано шлях до бази з каталогом (наприклад, `./data/nails_salon.db`):
    - Створити каталог `os.makedirs(db_dir, exist_ok=True)`.
    - Якщо `./nails_salon.db` існує в корені, а `./data/nails_salon.db` ще не існує — автоматично скопіювати/перемістити існуючу базу в `./data/nails_salon.db`, зберігаючи всі існуючі записи клієнтів.
- Оновити `.env.example`:
  ```ini
  BOT_TOKEN=your_bot_token_here
  ADMIN_IDS=[8607080614]
  ADMIN_USERNAME=@andriy_bot_dev
  DATABASE_URL=sqlite+aiosqlite:///./data/nails_salon.db
  SALON_NAME=Sense Nail Studio
  WEBAPP_URL=http://localhost:8000/app
  API_HOST=0.0.0.0
  API_PORT=8000
  APP_VERSION=1.0.1
  ```

---

## 4. Критерії приймання та валідація (Acceptance Criteria)
1. Ендпоінти `/api/admin/*` повертають `HTTP 403 Forbidden`, якщо запит надіслано без валідного підпису Telegram `initData` адміністратора (або некоректного `tg_id` у dev-режимі).
2. Запит з валідним `initData` адміністратора успішно проходить перевірку HMAC-SHA256 та отримує доступ до даних.
3. Ендпоінт `POST /api/bookings` захищено Rate Limiter (при спробі надіслати понад 5 запитів за 60 секунд повертається `HTTP 429 Too Many Requests`).
4. Ендпоінти `GET /health` та `GET /api/health` повертають `HTTP 200` з JSON-статусом підключення до бази даних.
5. Усі відповіді API містять захисні HTTP-заголовки (`X-Content-Type-Options: nosniff` тощо).
6. Фронтенд `frontend/src/api/client.ts` автоматично передає заголовок `X-Telegram-Init-Data`.
7. `Dockerfile` успішно збирає образ (Node 20 Vite build + Python 3.12 runtime) без помилок.
8. `docker-compose.yaml` коректно валідується (`podman compose config` / `docker compose config`) і налаштований з `restart: always` та збереженням `./data` і `./backups`.
9. Скрипт `scripts/backup.sh` виконується з кодом 0 та створює консистентний бекап у папці `backups/`.
10. Внутрішній бекап-сервіс `backup_service.py` успішно підключений до головного циклу `main.py`.
11. Зміни закомічені та відправлені до репозиторію:
    ```bash
    git add .
    git commit -m "feat: implement API security, rate limiting, docker-compose and automated backup"
    git push origin main
    ```
