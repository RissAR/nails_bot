# ТЕХНІЧНЕ ЗАВДАННЯ: Етап 7 — Імплементація дизайну «Варіант 1: Deep Sand & Caramel» у Telegram Mini App (Клієнт та Адмін)

## 1. Загальна інформація та мета етапу
- **Мета:**
  Оновити візуальну тему (кольорову гаму, глибину тіней та контраст) обох частин Telegram Mini App (клієнтської та адмінської) відповідно до затвердженого **Варіанту 1 (Deep Sand & Caramel)**. 
  - Гама робиться на **5–7% темнішою та щільнішою** (прибираємо занадто світлий вибілений фон).
  - Додається візуальна глибина: картки стають слоновою кісткою з теплими контурними рамками та м'якими кавовими тінями замість плоских сірих.
  - **СТРУКТУРА ТА ЛОГІКА НЕ ЗМІНЮЮТЬСЯ:** Усі кнопки, функціонал, структура компонентів, ендпоінти залишаються без змін — оновлюється **виключно дизайн та палітра**.
- **GitHub Repository:** `https://github.com/RissAR/nails_bot.git` (гілка `main`)
- **Стек:** React, Tailwind CSS, TypeScript, Vite.

---

## 2. Суворі правила виконання (Strict Scope Discipline)
1. **Zero Scope Creep:** Модифікувати тільки конфігурацію кольорів і стилів (`frontend/tailwind.config.js`, `frontend/src/index.css` та стилі тіней/рамок у компонентах). Не чіпати бізнес-логіку, кнопки чи обробники подій.
2. **Zero Hardcoded Secrets:** Усі токени суворо залишаються у `.env`.
3. **Автоматичний білд та Git:** Після оновлення обов'язково виконати збірку `npm run build` у папці `frontend/` та зафіксувати зміни:
   `git add . && git commit -m "feat(ui): implement Variant 1 Deep Sand & Caramel color palette and depth" && git push origin main`.

---

## 3. Специфікація палітри «Варіант 1: Deep Sand & Caramel»

### 3.1. Кольорова матриця (Tailwind & CSS):
- **Основний фон (Background):** `#F4ECE4` *(Теплий пісочний льон — на 6–7% темніший за старий #FDFBF7, без ядучого білого світла)*.
- **Поверхні та картки (Surface):** `#FAF7F2` *(М'яка слонова кістка замість чистого #FFFFFF)*.
- **Головний акцент / Кнопки (Primary):** `#C28751` *(Багата тепла карамельна бронза)*.
- **Hover стан кнопок (Primary Hover):** `#B37842` *(Глибша карамель при наведенні/натисканні)*.
- **Вторинний акцент / Бейджі (Accent / Badges):** `#EBD9C8` *(Теплий лате для виділення слотів, активних табів та бейджів)*.
- **Контурні рамки (Border):** `#E4D8CC` *(Теплий контур, що дає чітке відділення карток від пісочного фону)*.
- **Основний текст (Text Main):** `#231E1B` *(Глибокий темно-кавовий графіт для ідеального контрасту)*.
- **Допоміжний текст (Text Muted):** `#6E6157` *(Тепле мокко для тайм-міток, тривалості та другорядних деталей)*.
- **Зелений статус (Success/Sterile):** `#3E6B48` та `#E2EBE4`.

### 3.2. М'які теплі тіні (Elevation & Depth):
Додати в `tailwind.config.js` кастомні тіні з теплим кавовим відтінком замість холодних сірих:
```javascript
boxShadow: {
  'card': '0 4px 16px rgba(60, 40, 25, 0.06)',
  'card-active': '0 8px 24px rgba(60, 40, 25, 0.10)',
  'dock': '0 -4px 20px rgba(60, 40, 25, 0.08)',
}
```

---

## 4. Конкретні файли для оновлення

### 4.1. `frontend/tailwind.config.js`:
Оновити секцію `theme.extend`:
```javascript
colors: {
  nude: {
    bg: '#F4ECE4',           // Теплий пісочний льон (5-7% темніший)
    surface: '#FAF7F2',      // М'яка слонова кістка
    primary: '#C28751',      // Карамельна бронза
    primaryHover: '#B37842', // Насичена карамель
    accent: '#EBD9C8',       // Теплий лате / активні чіпси
    secondary: '#E8DDD3',    // Нейтральний лате
    border: '#E4D8CC',       // Теплий контурний бордер
    text: '#231E1B',         // Глибокий еспресо-графіт
    muted: '#6E6157',        // Тепле мокко
    green: '#3E6B48',
    greenLight: '#E2EBE4',
  }
},
boxShadow: {
  'card': '0 4px 16px rgba(60, 40, 25, 0.06)',
  'card-active': '0 8px 24px rgba(60, 40, 25, 0.10)',
  'dock': '0 -4px 20px rgba(60, 40, 25, 0.08)',
}
```

### 4.2. `frontend/src/index.css`:
- Оновити глобальний фон та текст `body`:
  ```css
  body {
    margin: 0;
    padding: 0;
    background-color: #F4ECE4;
    color: #231E1B;
    -webkit-tap-highlight-color: transparent;
    user-select: none;
  }

  ::-webkit-scrollbar-thumb {
    background: #E4D8CC;
    border-radius: 4px;
  }

  ::-webkit-scrollbar-thumb:hover {
    background: #C28751;
  }
  ```

### 4.3. Візуальна глибина в компонентах:
- У картках послуг (`ServiceList.tsx`), майстрів (`MasterList.tsx`), календаря (`SlotPicker.tsx`), модалки (`BookingModal.tsx`) та блоках адмін-панелі (`AdminDashboard.tsx`):
  - Переконатися, що використовується клас тіні `shadow-card` або `shadow-sm` на фоні `bg-nude-surface` та `border border-nude-border`.
  - Нижня закріплена плашка (Sticky Booking Bar) використовує фон `bg-[#F4ECE4]/95 backdrop-blur-md border-t border-nude-border shadow-dock`.

---

## 5. Критерії приймання та валідація (Acceptance Criteria)
1. Фон обох Mini App (клієнтської та адмінської) став приємним, теплим пісочно-лляним (`#F4ECE4`), не сліпить очі.
2. Картки чітко виділяються завдяки кольору слонової кістки (`#FAF7F2`), теплому бордеру та м'яким кавовим тіням, додаючи глибини інтерфейсу.
3. Кнопки та активні слоти мають благородний карамельний відтінок (`#C28751`).
4. Жодна кнопка, обробник чи елемент функціоналу не зламані.
5. `npm run build` у папці `frontend/` збирається з кодом 0, файли у `dist` оновлені.
6. Зміни закомічені та відправлені на GitHub:
   ```bash
   git add .
   git commit -m "feat(ui): implement Variant 1 Deep Sand & Caramel color palette and depth"
   git push origin main
   ```
