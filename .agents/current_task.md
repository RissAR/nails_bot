# ТЕХНІЧНЕ ЗАВДАННЯ: Етап 3 — Налаштування інлайн-кнопок Mini App, Menu Button та запуск локального демона для тестування

## 1. Загальна інформація та мета етапу
- **Мета:** 
  1. Забезпечити повне покриття інлайн-кнопками запуску Telegram Mini App (TMA) у всіх діалогах клієнта та адміністратора.
  2. Додати постійну нативну кнопку Telegram Menu Button (`MenuButtonWebApp`) у лівому кутку поля вводу, щоб Mini App відкривався в 1 клік без пошуку повідомлень.
  3. Підготувати систему до запуску в режимі локального демона (фонового процесу) для безперебійного тестування.
- **GitHub Repository:** `https://github.com/RissAR/nails_bot.git` (гілка `main`)
- **Стек:** aiogram 3.x, FastAPI, Uvicorn, React Mini App.

---

## 2. Суворі правила виконання (Strict Scope Discipline)
1. **Zero Hardcoded Secrets (КРИТИЧНО):** `BOT_TOKEN` та інші конфіденційні дані зчитуються **виключно з локального `.env`**. Заборонено записувати токени у файли коду.
2. **Zero Scope Creep:** Модифікувати лише клавіатури, налаштування Menu Button у `main.py`, хендлери та конфігурацію URL.
3. **Git Автоматизація:** Після завершення роботи виконати:
   `git add . && git commit -m "feat: configure WebApp inline buttons, chat menu button and daemon setup" && git push origin main`.

---

## 3. Деталі технічної реалізації

### 3.1. Інлайн-кнопки для Клієнта (`src/keyboards/client_kb.py`)
- **Головне меню (`get_client_main_kb`):**
  - Перша основна кнопка на всю ширину: `💅 Записатися онлайн (Mini App)` з `web_app=WebAppInfo(url=settings.WEBAPP_URL)`.
- **Список категорій (`get_categories_kb`):**
  - Кнопка `💅 Відкрити Mini App` з `web_app=WebAppInfo(url=settings.WEBAPP_URL)`.
- **Список послуг конкретної категорії (`get_category_services_kb`):**
  - Кнопка швидкого запису `💅 Записатися в Mini App`.
- **Детальна картка обраної послуги (`get_service_detail_kb`):**
  - Кнопка `✨ Записатися на цю послугу` з посиланням:
    `web_app=WebAppInfo(url=f"{settings.WEBAPP_URL}?service_id={service_id}")`.

### 3.2. Інлайн-кнопки для Адміністратора (`src/keyboards/admin_kb.py`)
- **Головна панель адміна (`get_admin_main_kb`):**
  - Кнопка на всю ширину `📱 Відкрити адмін-панель TMA` з `web_app=WebAppInfo(url=f"{settings.WEBAPP_URL}?role=admin")`.
- **У підменю повернення (`get_admin_back_kb`):**
  - Також дублювати кнопку швидкого відкриття `📱 Адмін-панель TMA`.

### 3.3. Нативна кнопка меню Telegram (`MenuButtonWebApp`) у `src/main.py`
- При старті бота в функції `main()` або `run_bot()` встановити постійну кнопку меню чату:
  ```python
  from aiogram.types import MenuButtonWebApp, WebAppInfo

  await bot.set_chat_menu_button(
      menu_button=MenuButtonWebApp(
          text="💅 Запис",
          web_app=WebAppInfo(url=settings.WEBAPP_URL),
      )
  )
  ```
- Це створює нативну кнопку зліва від поля вводу тексту ("💅 Запис"), за якою користувач завжди може відкрити Mini App в 1 тап.

### 3.4. Конфігурація URL (`src/config.py` та `.env`)
- `WEBAPP_URL` зчитується з `.env`. За замовчуванням `http://localhost:8000/app`.
- Якщо користувач запускає тунель (ngrok / cloudflared) і додає в `.env` рядок типу `WEBAPP_URL=https://abc.ngrok-free.app/app`, бот миттєво підхоплює HTTPS-посилання, що дозволяє відкривати Mini App на реальному смартфоні в Telegram!

---

## 4. Локальний запуск як демон та тестування
- Створити зручний скрипт запуску або інструкцію для фонового демона:
  ```bash
  # Запуск у фоновому режимі (демон):
  nohup python -m src.main > app.log 2>&1 &
  ```
- Перевірка працездатності:
  1. Бекенд API: `curl http://localhost:8000/api/services` (повертає JSON послуг).
  2. Фронтенд Mini App: `curl -I http://localhost:8000/app` (повертає HTTP 200 OK з HTML сторінкою).
  3. Бот: команда `/start` відправляє інлайн-кнопку з WebAppInfo та налаштовує MenuButton.

---

## 5. Критерії приймання та валідація (Acceptance Criteria)
1. Усі інлайн-клавіатури клієнта та адміна містять валідні кнопки `WebAppInfo`.
2. У `main.py` налаштовано `bot.set_chat_menu_button(...)`.
3. Код проходить компіляцію без помилок (`python -m py_compile src/**/*.py`).
4. Зміни закомічені та відправлені на GitHub:
   ```bash
   git add .
   git commit -m "feat: configure WebApp inline buttons, chat menu button and daemon setup"
   git push origin main
   ```
