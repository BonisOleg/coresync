# CoreSync Brand Style Guide

## 📋 ЗАГАЛЬНА ІНФОРМАЦІЯ

### Бренд
**CoreSync** - сучасний спа-центр з передовими технологіями, що поєднує розкіш з інноваціями для створення неперевершеного досвіду релаксації.

### Основні Принципи Дизайну
- **Мінімалізм** - чистота та простота форм
- **Технологічність** - сучасний, високотехнологічний вигляд
- **Розкіш** - преміальне відчуття якості
- **Гармонія** - баланс між природою та технологіями
- **Доступність** - зручність для всіх користувачів

---

## 🎨 КОЛІРНА ПАЛІТРА

### Основні Кольори
```css
/* Основний темно-синій - елегантність та довіра */
--primary-dark: #1A2635;

/* Основний синій - професійність та спокій */
--primary-main: #2D4A6B;

/* Світлий синій - свіжість та чистота */
--primary-light: #4A6B8C;

/* Акцентний золотий - розкіш та преміальність */
--accent-gold: #B8860B;

/* Світлий золотий - тепло та гостинність */
--accent-light: #DAA520;

/* Темний золотий - глибина та багатство */
--accent-dark: #8B7109;
```

### Нейтральні Кольори
```css
/* Білий - чистота та простір */
--white: #FFFFFF;

/* Темний - контрастність та читабельність */
--black: #000000;

/* Сірі тони для тексту та фонів */
--gray-900: #111827;
--gray-800: #1F2937;
--gray-700: #374151;
--gray-600: #4B5563;
--gray-500: #6B7280;
--gray-400: #9CA3AF;
--gray-300: #D1D5DB;
--gray-200: #E5E7EB;
--gray-100: #F3F4F6;
--gray-50: #F9FAFB;
```

### Семантичні Кольори
```css
/* Успіх - для підтверджень та позитивних дій */
--success: #10B981;

/* Попередження - для важливих повідомлень */
--warning: #F59E0B;

/* Помилка - для помилок та критичних дій */
--error: #EF4444;

/* Інформація - для додаткової інформації */
--info: #3B82F6;
```

---

## 🔤 ТИПОГРАФІКА

### Шрифтова Система
```css
/* Основний шрифт для тексту */
--font-primary: 'Maison Neue Book', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

/* Заголовки та важливий текст */
--font-headings: 'Maison Neue Bold', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

/* Моноширинний для коду та технічної інформації */
--font-mono: 'Maison Neue Mono', 'Monaco', 'Consolas', monospace;

/* Декоративний для особливих заголовків */
--font-display: 'Mekgen', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

### Розміри Шрифтів
```css
/* Заголовки */
--text-6xl: 3.75rem;  /* 60px - Великі герої заголовки */
--text-5xl: 3rem;     /* 48px - Основні заголовки */
--text-4xl: 2.25rem;  /* 36px - Вторинні заголовки */
--text-3xl: 1.875rem; /* 30px - Третинні заголовки */
--text-2xl: 1.5rem;   /* 24px - Великі підзаголовки */
--text-xl: 1.25rem;   /* 20px - Підзаголовки */

/* Основний текст */
--text-lg: 1.125rem;  /* 18px - Великий основний текст */
--text-base: 1rem;    /* 16px - Стандартний текст */
--text-sm: 0.875rem;  /* 14px - Малий текст */
--text-xs: 0.75rem;   /* 12px - Дуже малий текст */
```

### Жирність Шрифту
```css
--font-light: 300;
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
--font-extrabold: 800;
```

### Висота Рядка
```css
--leading-none: 1;
--leading-tight: 1.25;
--leading-snug: 1.375;
--leading-normal: 1.5;
--leading-relaxed: 1.625;
--leading-loose: 2;
```

---

## 📐 ПРОСТОРОВА СИСТЕМА

### Відступи та Відстані
```css
--space-0: 0;
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */
--space-24: 6rem;     /* 96px */
--space-32: 8rem;     /* 128px */
--space-40: 10rem;    /* 160px */
--space-48: 12rem;    /* 192px */
--space-56: 14rem;    /* 224px */
--space-64: 16rem;    /* 256px */
```

### Контейнери
```css
--container-sm: 640px;
--container-md: 768px;
--container-lg: 1024px;
--container-xl: 1280px;
--container-2xl: 1536px;
```

---

## 🔲 КОМПОНЕНТИ

### Радіуси Заокруглення
```css
--radius-none: 0;
--radius-sm: 0.125rem;   /* 2px */
--radius-base: 0.25rem;  /* 4px */
--radius-md: 0.375rem;   /* 6px */
--radius-lg: 0.5rem;     /* 8px */
--radius-xl: 0.75rem;    /* 12px */
--radius-2xl: 1rem;      /* 16px */
--radius-3xl: 1.5rem;    /* 24px */
--radius-full: 9999px;
```

### Тіні
```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-base: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
```

---

## 🎭 АНІМАЦІЇ ТА ПЕРЕХОДИ

### Часові Функції
```css
--transition-fast: 150ms ease-in-out;
--transition-base: 250ms ease-in-out;
--transition-slow: 400ms ease-in-out;
--transition-slower: 600ms ease-in-out;
```

### Криві Безьє
```css
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

---

## 📱 АДАПТИВНІСТЬ

### Точки Зламу (Breakpoints)
```css
--breakpoint-sm: 640px;   /* Мобільні пристрої (великі) */
--breakpoint-md: 768px;   /* Планшети */
--breakpoint-lg: 1024px;  /* Ноутбуки */
--breakpoint-xl: 1280px;  /* Десктопи */
--breakpoint-2xl: 1536px; /* Великі десктопи */
```

### Медіа-запити
```css
/* Мобільні пристрої */
@media (max-width: 767px) { /* Стилі для мобільних */ }

/* Планшети */
@media (min-width: 768px) and (max-width: 1023px) { /* Стилі для планшетів */ }

/* Десктопи */
@media (min-width: 1024px) { /* Стилі для десктопів */ }

/* iOS Safari специфічні */
@supports (-webkit-touch-callout: none) { /* iOS специфічні стилі */ }
```

---

## 🎯 ПРИНЦИПИ ВИКОРИСТАННЯ

### Ієрархія Кольорів
1. **Основний (Primary)** - для головних елементів навігації та CTA
2. **Акцентний (Accent)** - для виділення важливих елементів
3. **Нейтральний (Gray)** - для тексту та фонових елементів
4. **Семантичний** - для статусів та повідомлень

### Типографічна Ієрархія
1. **H1** - Головні заголовки сторінок (text-5xl/text-6xl)
2. **H2** - Секції контенту (text-3xl/text-4xl)
3. **H3** - Підсекції (text-2xl/text-3xl)
4. **H4-H6** - Менші заголовки (text-xl та менше)
5. **Body** - Основний текст (text-base/text-lg)
6. **Caption** - Підписи та примітки (text-sm/text-xs)

### Правила Доступності
- Мінімальний контраст 4.5:1 для основного тексту
- Мінімальний контраст 3:1 для великого тексту
- Мінімальний розмір сенсорних цілей 44px для iOS Safari
- Підтримка screen readers через семантичну HTML структуру

---

## 🚀 ПРАКТИЧНІ РЕКОМЕНДАЦІЇ

### Що РОБИТИ
✅ Використовувати CSS кастомні властивості (CSS Variables)
✅ Зберігати консистентність у відступах (система 4px)
✅ Застосовувати семантичні назви класів
✅ Оптимізувати для мобільних пристроїв (Mobile First)
✅ Використовувати прогресивне покращення
✅ Тестувати на реальних пристроях

### Що НЕ РОБИТИ
❌ Використовувати !important (тільки у крайніх випадках)
❌ Інлайнові стилі в HTML
❌ Жорстко задані значення замість змінних
❌ Конфліктуючі селектори з однаковою специфічністю
❌ Переоптимізація (premature optimization)
❌ Ігнорування доступності

---

## 📖 ПРИКЛАДИ ВИКОРИСТАННЯ

### Кнопки
```css
/* Основна кнопка */
.btn-primary {
    background: var(--primary-main);
    color: var(--white);
    padding: var(--space-3) var(--space-6);
    border-radius: var(--radius-lg);
    font-family: var(--font-headings);
    font-weight: var(--font-medium);
    transition: var(--transition-fast);
}

.btn-primary:hover {
    background: var(--primary-dark);
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}
```

### Картки
```css
.card {
    background: var(--white);
    border-radius: var(--radius-2xl);
    box-shadow: var(--shadow-base);
    padding: var(--space-6);
    transition: var(--transition-base);
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-xl);
}
```

### Типографіка
```css
.heading-1 {
    font-family: var(--font-headings);
    font-size: var(--text-5xl);
    font-weight: var(--font-bold);
    line-height: var(--leading-tight);
    color: var(--gray-900);
}

.body-text {
    font-family: var(--font-primary);
    font-size: var(--text-base);
    line-height: var(--leading-normal);
    color: var(--gray-700);
}
```

---

*Цей style guide створено на основі брендових матеріалів CoreSync для забезпечення консистентного та якісного користувацького досвіду на всіх платформах.*
