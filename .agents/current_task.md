# ТЕХНІЧНЕ ЗАВДАННЯ: Етап 8 — Комплексне вирішення жорсткого кешування Telegram Mini App (Cache-Busting & Storage Management)

## 1. Загальна інформація та мета етапу
- **Мета:** Повністю усунути проблему жорсткого кешування Telegram WebView, через яку клієнти можуть бачити застарілий інтерфейс або накопичувати десятки мегабайтів кешу. Впровадити трирівневу систему скидання та контролю кешування:
  1. **HTTP Cache-Control заголовки на рівні FastAPI:** Сувора заборона кешування для `index.html` (`no-cache, no-store, must-revalidate`) та довготривале кешування для зхешованих Vite асетів (`/assets/*`).
  2. **Cache-Busting параметр у боті:** Автоматичне додавання версійного параметра `?v={APP_VERSION}` до всіх URL-посилань запуску Mini App (інлайн-кнопки та Menu Button), що примушує Telegram WebView негайно скидати застарілий кеш при зміні версії.
  3. **Клієнтський скрипт автоочищення кешу та пам'яті (Frontend):** Автоматичне видалення старих Service Worker/браузерних кешів (`caches.delete()`) та моніторинг розміру локального сховища при зміні версії додатку.
- **GitHub Repository:** `https://github.com/RissAR/nails_bot.git` (гілка `main`)
- **Стек:** FastAPI, Python (aiogram 3.x), React, Vite, TypeScript.

---

## 2. Суворі правила виконання (Strict Scope Discipline)
1. **Zero Hardcoded Secrets (КРИТИЧНО):** `BOT_TOKEN` та інші конфіденційні дані зчитуються **виключно з локального `.env`**. Заборонено записувати токени у файли коду.
2. **Zero Scope Creep:** Модифікувати тільки роздачу статики у `src/api/app.py`, версійну конфігурацію в `src/config.py`, клавіатури бота та стартову ініціалізацію у `frontend/src/main.tsx`. Не чіпати бізнес-логіку або розрахунок цін/слотів.
3. **Git Автоматизація:** Після завершення роботи та перевірки виконати:
   `git add . && git commit -m "feat: implement 3-tier Telegram Mini App cache-busting and storage cleanup" && git push origin main`.

---

## 3. Деталі технічної реалізації

### 3.1. Рівень 1: Серверні HTTP-заголовки у FastAPI (`src/api/app.py`)
Зараз `app.mount("/app", StaticFiles(directory=dist_path, html=True))` віддає `index.html` без суворих заголовків кешування, через що Telegram WebView кешує його на невизначений термін.

**Необхідні зміни у `src/api/app.py`:**
1. Для роздачі `index.html` (маршрути `/app`, `/app/` та будь-які fallback роути):
   - Повертати `FileResponse` з обов'язковими HTTP-заголовками проти кешування:
     ```python
     headers = {
         "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
         "Pragma": "no-cache",
         "Expires": "0",
     }
     ```
2. Для папки зхешованих асетів (`dist/assets` з файлами `index-[hash].js`, `index-[hash].css`):
   - Монтувати окремо під маршрут `/app/assets`:
     - Оскільки Vite додає унікальний хеш у назву кожного бандла, ці файли безпечно кешувати:
       `Cache-Control: public, max-age=31536000, immutable`.
3. Створити кастомний `StaticFiles` або middleware, який автоматично встановлює ці заголовки залежно від типу файлу (`text/html` ➔ `no-store`, `application/javascript` / `text/css` ➔ `immutable`).

---

### 3.2. Рівень 2: Cache-Busting параметр у боті (`src/config.py`, `keyboards`, `main.py`)

1. **Конфігурація версії (`src/config.py`):**
   - Додати поле `APP_VERSION: str = "1.0.1"` (зчитується з `.env` з можливістю швидкого перевизначення).
   - Створити хелпер-метод у `Settings`:
     ```python
     def get_webapp_url(self, extra_params: dict[str, str] | None = None) -> str:
         """Generate WebApp URL with cache-busting version parameter."""
         params = {"v": self.APP_VERSION}
         if extra_params:
             params.update(extra_params)
         query = "&".join(f"{k}={v}" for k, v in params.items())
         base = self.WEBAPP_URL.rstrip("/")
         sep = "&" if "?" in base else "?"
         return f"{base}{sep}{query}"
     ```

2. **Оновлення всіх викликів `WebAppInfo` у боті:**
   - У `src/keyboards/client_kb.py`:
     - Головне меню: `web_app=WebAppInfo(url=settings.get_webapp_url())`.
     - Запис на конкретну послугу: `web_app=WebAppInfo(url=settings.get_webapp_url({"service_id": str(service_id)}))`.
   - У `src/keyboards/admin_kb.py`:
     - Адмін-кнопка: `web_app=WebAppInfo(url=settings.get_webapp_url({"role": "admin"}))`.
   - У `src/main.py`:
     - `bot.set_chat_menu_button`:
       `menu_button=MenuButtonWebApp(text="💅 Запис", web_app=WebAppInfo(url=settings.get_webapp_url()))`.

*Результат:* Коли версія в `.env` змінюється на нову (наприклад, `1.0.2`), Telegram WebView сприймає URL як новий і гарантовано завантажує свіжий `index.html`.

---

### 3.3. Рівень 3: Клієнтське автоочищення кешу та пам'яті (`frontend/src/main.tsx`)

У точці входу клієнтського додатку (`frontend/src/main.tsx`) перед рендером React додати легкий механізм очищення:

1. **Очищення при зміні версії:**
   - Отримати версію з URL (параметр `?v=...`) або із зашитого `package.json` / Vite env.
   - Перевірити `localStorage.getItem('sense_app_version')`.
   - Якщо версія відрізняється:
     ```javascript
     // 1. Очищення браузерного Cache Storage
     if ('caches' in window) {
       caches.keys().then((names) => {
         names.forEach((name) => caches.delete(name));
       });
     }
     // 2. Очищення застарілих тимчасових даних
     const keysToRemove = [];
     for (let i = 0; i < localStorage.length; i++) {
       const key = localStorage.key(i);
       if (key && !key.startsWith('sense_essential_')) {
         keysToRemove.push(key);
       }
     }
     keysToRemove.forEach((k) => localStorage.removeItem(k));
     localStorage.setItem('sense_app_version', currentVersion);
     ```

2. **Захист від переповнення пам'яті (Ліміт сховища):**
   - Перевіряти сумарний розмір `localStorage`: якщо обсяг перевищує безпечний ліміт (~10–20 МБ через накопичені логи), скидати застарілі тимчасові дані.

---

## 4. Критерії приймання та валідація (Acceptance Criteria)
1. При запиті `curl -I http://localhost:8000/app/` у відповіді присутні заголовки:
   `Cache-Control: no-cache, no-store, must-revalidate, max-age=0` (або аналогічні суворі `no-store`).
2. Для асетів `curl -I http://localhost:8000/app/assets/index-....js` повертаються оптимізовані заголовки кешування.
3. Усі кнопки бота (`client_kb`, `admin_kb`, `MenuButtonWebApp`) формують URL із версійним суфіксом `?v=...`.
4. При відкритті Mini App клієнтський скрипт очищає застарілі кеші у `caches` та оновлює `sense_app_version`.
5. `npm run build` у `frontend/` збирається без помилок (код 0).
6. Усі секрети завантажуються виключно з `.env`.
7. Зміни закомічені та відправлені на GitHub:
   ```bash
   git add .
   git commit -m "feat: implement 3-tier Telegram Mini App cache-busting and storage cleanup"
   git push origin main
   ```
