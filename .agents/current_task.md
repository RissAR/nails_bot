# ТЕХНІЧНЕ ЗАВДАННЯ: Етап 13 — Редизайн Telegram Mini App у стилі «Silk & Caramel» (Варіант Б)

## 1. Загальна інформація та мета етапу
- **Мета:**
  - Оновити зовнішній вигляд Telegram Mini App клієнта та адміна, додавши візуальну глибину, світлотінь та тактильний об'єм у стилі **«Silk & Caramel» (Варіант Б)** замість попереднього плоского вигляду.
  - **СУВОРЕ ПРАВИЛО:**
    - Змінюється **виключно дизайн та кольорова обробка (градієнти, тіні, бліки, скло)**.
    - **НЕ чіпати** розташування кнопок, структуру, розміри, сітку, відступи, тексти чи бізнес-логіку.
    - Усі хуки React оголошуються суворо на початку компонентів (Rules of Hooks).
- **GitHub Repository:** `https://github.com/RissAR/nails_bot.git` (гілка `main`)
- **Стек:** React, TypeScript, Tailwind CSS, Vite.

---

## 2. Суворі правила безпеки та дисципліни (Strict Scope Discipline)
1. **Zero Layout Shift:**
   - Заборонено змінювати функціонал, порядок відображення, висоту чи розташування кнопок.
   - Усі розміри (`py-2.5`, `px-4`, `rounded-xl`, `grid-cols-2` тощо) залишаються незмінними.
2. **Zero Scope Creep:**
   - Зміни вносяться **виключно у файли фронтенду**:
     - `frontend/src/index.css`
     - `frontend/tailwind.config.js`
     - `frontend/src/App.tsx`
     - `frontend/src/components/Header.tsx`
     - `frontend/src/components/ServiceList.tsx`
     - `frontend/src/components/MasterList.tsx`
     - `frontend/src/components/SlotPicker.tsx`
     - `frontend/src/components/BookingModal.tsx`
     - `frontend/src/components/AdminDashboard.tsx`
   - Бекенд (`src/`) та база даних не чіпаються.
3. **Збірка:**
   - Після внесення змін виконати `npm run build` у папці `frontend/` та переконатися в успішній компіляції (exit code 0).
4. **Git Автоматизація:**
   - Після завершення та перевірки виконати:
     `git add . && git commit -m "feat: apply Silk and Caramel tactile design aesthetic across Mini App" && git push origin main`.

---

## 3. Деталі технічної реалізації «Silk & Caramel»

### 3.1. Глобальні стилі та класи глибини (`frontend/src/index.css`)

1. **Фонове освітлення (Ambient Gradient Canvas):**
   - Замість плоского однорідного `#F4ECE4` налаштувати для `body`:
     ```css
     body {
       margin: 0;
       padding: 0;
       background: radial-gradient(circle at 50% 0%, #FDF9F5 0%, #F5ECE3 50%, #ECE0D2 100%) fixed;
       background-color: #F4ECE4;
       color: #231E1B;
       -webkit-tap-highlight-color: transparent;
       user-select: none;
     }
     ```
   - Це створює відчуття м'якого студійного світла зверху, позбавляючи екран ефекту плоского паперу.

2. **Базові класи глибини (Utility Classes):**
   Додати до `frontend/src/index.css`:
   ```css
   /* Керамічна картка (звичайний стан) */
   .card-ceramic {
     background: linear-gradient(180deg, #FFFFFF 0%, #FAF5EE 100%);
     box-shadow: 0 4px 16px rgba(60, 40, 25, 0.05), inset 0 1px 0 rgba(255, 255, 255, 0.95);
     border: 1px solid rgba(228, 216, 204, 0.7);
   }

   /* Керамічна картка (активний / обраний стан) */
   .card-ceramic-active {
     background: linear-gradient(180deg, #FFFDFB 0%, #F6ECE0 100%);
     box-shadow: 0 8px 24px rgba(194, 135, 81, 0.16), inset 0 1px 0 rgba(255, 255, 255, 1);
     border: 1.5px solid #C28751;
   }

   /* Тактильна кнопка дії Карамель (3D Bevel & Ambient Shadow) */
   .btn-caramel-3d {
     background: linear-gradient(180deg, #D49660 0%, #B7763B 100%);
     box-shadow: 0 6px 18px rgba(183, 118, 59, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.35);
   }
   .btn-caramel-3d:active {
     transform: translateY(1px);
     box-shadow: 0 2px 8px rgba(183, 118, 59, 0.25), inset 0 1px 0 rgba(0, 0, 0, 0.1);
   }

   /* Активний таб / чіпс */
   .chip-active-3d {
     background: linear-gradient(180deg, #D49660 0%, #B7763B 100%);
     box-shadow: 0 3px 10px rgba(183, 118, 59, 0.22), inset 0 1px 0 rgba(255, 255, 255, 0.28);
   }

   /* Ефект матового скла (Frosted Glass) для шапки та закріпленого доку */
   .glass-nav {
     backdrop-filter: blur(14px);
     -webkit-backdrop-filter: blur(14px);
     background: rgba(250, 247, 242, 0.85);
     border-bottom: 1px solid rgba(228, 216, 204, 0.6);
   }
   
   .glass-dock {
     backdrop-filter: blur(16px);
     -webkit-backdrop-filter: blur(16px);
     background: rgba(250, 247, 242, 0.88);
     border-top: 1px solid rgba(228, 216, 204, 0.7);
     box-shadow: 0 -8px 24px rgba(60, 40, 25, 0.06);
   }
   ```

---

### 3.2. Точкове застосування у компонентах

1. **`frontend/src/components/Header.tsx`:**
   - На елемент `<header>` замість `bg-nude-surface border-b border-nude-border` застосувати клас `glass-nav`.
   - Значок Sparkles в колі: додати легкий вертикальний градієнт `bg-gradient-to-br from-[#FAF5EE] to-[#EBD9C8] border border-[#C28751]/20`.

2. **`frontend/src/components/ServiceList.tsx`:**
   - **Таби категорій (Filter Tabs):**
     - Активний таб: клас `chip-active-3d text-white` замість плоского `bg-nude-primary`.
     - Неактивні таби: `card-ceramic text-nude-muted hover:text-nude-text`.
   - **Плитки послуг:**
     - Звичайний стан: клас `card-ceramic hover:border-nude-primary/50`.
     - Обраний стан (`isSelected`): клас `card-ceramic-active`.
     - Індикатор (радіо-кружечок): при `isSelected` використовувати `bg-gradient-to-br from-[#D49660] to-[#B7763B]` з білою точкою.

3. **`frontend/src/components/MasterList.tsx`:**
   - **Картки майстрів:**
     - Звичайний стан: клас `card-ceramic hover:border-nude-primary/50`.
     - Обраний стан (`isSelected`): клас `card-ceramic-active`.
     - Аватар майстра (круг з першою літерою):
       - При `isSelected`: `bg-gradient-to-br from-[#D49660] to-[#B7763B] text-white shadow-sm`.
       - При звичайному: `bg-gradient-to-br from-[#FAF5EE] to-[#EBD9C8] text-nude-primary border border-nude-border/60`.

4. **`frontend/src/components/SlotPicker.tsx`:**
   - **Календарні дні (Date Buttons):**
     - Обраний день: `btn-caramel-3d text-white font-bold`.
     - Звичайний день: `card-ceramic text-nude-text hover:border-nude-primary/40`.
   - **Часові слоти (Time Slots):**
     - Обраний слот: `btn-caramel-3d text-white font-bold shadow-sm`.
     - Вільний слот: `card-ceramic text-nude-text hover:border-nude-primary/50`.

5. **`frontend/src/App.tsx`:**
   - **Закріплена нижня планка (Sticky Bottom Bar):**
     - Контейнер: замінити `bg-[#F4ECE4]/95` на `glass-dock`.
     - Головна кнопка дії («Записатися»):
       - Активний стан (коли час обрано): застосувати клас `btn-caramel-3d text-white active:scale-95` замість плоского `bg-nude-primary`.
       - Неактивний стан («Оберіть час»): `bg-nude-border/70 text-nude-muted/80 cursor-not-allowed`.

6. **`frontend/src/components/BookingModal.tsx`:**
   - Модальне вікно (діалог):
     - Внутрішній блок модалки: застосувати легкий керамічний градієнт `bg-gradient-to-b from-[#FFFFFF] to-[#FAF5EE] border border-nude-border shadow-2xl`.
     - Кнопка підтвердження «Підтвердити запис»: застосувати `btn-caramel-3d text-white`.

7. **`frontend/src/components/AdminDashboard.tsx`:**
   - Картки метрик (Pending, Today, Revenue, Clients):
     - Замінити `bg-nude-surface border-nude-border` на `card-ceramic`.
   - Картки записів:
     - Замінити плоскі фони на `card-ceramic` з акцентними кольоровими статусами.
   - Кнопки дій адміна («Підтвердити», «Відхилити»): додати легкі бліки та глибину.

---

## 4. Критерії приймання та валідація (Acceptance Criteria)
1. Усі компоненти Telegram Mini App отримали тактильну глибину «Silk & Caramel»:
   - Фон екрана має м'який студійний перехід світла (Ambient Radial Gradient).
   - Кнопки дій мають соковитий мікроградієнт карамелі з верхнім бліком (3D Bevel) та розсіяною тінню.
   - Картки послуг і майстрів мають керамічний біло-перламутровий перехід, а обрані — золотисто-карамельний контур та підняту тінь.
   - Шапка та нижній закріплений док мають матове розмиття скла (`glass-nav`, `glass-dock`).
2. Жодна кнопка, відступ чи сітка не змінили свого розміру чи розташування (Zero Layout Shift).
3. `npm run build` у папці `frontend/` успішно завершується з кодом 0, генеруючи оновлені асети в `dist/`.
4. Зміни закомічені та відправлені до репозиторію:
   ```bash
   git add .
   git commit -m "feat: apply Silk and Caramel tactile design aesthetic across Mini App"
   git push origin main
   ```
