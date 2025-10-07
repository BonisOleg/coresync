# 📋 ПОВНИЙ АНАЛІЗ ДЕСКТОПНОГО МЕНЮ

## 📅 Дата: 7 жовтня 2025

---

## 🎯 СТРУКТУРА ДЕСКТОПНОГО МЕНЮ

На скріншоті видно горизонтальне меню з такими елементами:

```
[MEMBERSHIP] [CONTACTS] [MY ACCOUNT]  [CORESYNC LOGO]  [MENSUITE] [CORESYNC PRIVATE] [BOOK NOW] [X]
       ↑ Ліва частина                      ↑ Центр              ↑ Права частина            ↑ Бургер
```

---

## 🗂️ 1. HTML СТРУКТУРА

### Файл: `/coresync_backend/templates/base.html` (рядки 17-51)

```html
<!-- Header -->
<header class="header">
    <div class="container">
        <!-- Логотип в центрі -->
        <div class="header-logo">
            <a href="{% url 'home' %}">
                <img src="{% static 'images/menu.png' %}" alt="CORESYNC" class="header-logo-img">
            </a>
        </div>

        <!-- Navigation Menu -->
        <nav class="nav-menu" id="nav-menu">
            <!-- Ліва частина меню -->
            <div class="nav-left">
                <button class="nav-btn" data-link="{% url 'membership' %}">Membership</button>
                <button class="nav-btn" data-link="{% url 'contacts' %}">Contacts</button>
                {% if user.is_authenticated %}
                <button class="nav-btn" data-link="/dashboard/">My Account</button>
                {% else %}
                <button class="nav-btn" data-link="/signup/">Sign Up</button>
                <button class="nav-btn" data-link="/login/">Sign In</button>
                {% endif %}
            </div>
            
            <!-- Права частина меню -->
            <div class="nav-right">
                <button class="nav-btn" data-link="{% url 'menssuite' %}">Mensuite</button>
                <button class="nav-btn" data-link="{% url 'private' %}">Coresync Private</button>
                <button class="nav-btn nav-btn--book" data-link="{% url 'booking_calendar' %}">BOOK NOW</button>
            </div>
        </nav>

        <!-- Бургер меню (для мобільних/планшетів) -->
        <div class="burger-menu" id="burger-menu">
            <span class="burger-line"></span>
            <span class="burger-line"></span>
            <span class="burger-line"></span>
        </div>
    </div>
</header>
```

### Компоненти HTML:

1. **`.header`** - контейнер header
2. **`.header-logo`** - логотип CORESYNC в центрі
3. **`.nav-menu`** - контейнер навігації (показується при кліку на бургер)
4. **`.nav-left`** - ліва частина меню (Membership, Contacts, My Account)
5. **`.nav-right`** - права частина меню (Mensuite, Private, Book Now)
6. **`.nav-btn`** - кнопки навігації
7. **`.nav-btn--book`** - спеціальна кнопка "BOOK NOW" з бежевим фоном
8. **`.burger-menu`** - іконка бургер меню (3 лінії)

---

## 🎨 2. CSS СТИЛІ

### Файл: `/coresync_backend/static/css/styles.css`

#### A) Header контейнер (рядки 37-65)

```css
.header {
    position: fixed;              /* Фіксоване положення вгорі */
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;               /* Над усім контентом */
    padding: 2rem 0;
    background: rgba(0, 0, 0, .9);  /* Напівпрозорий чорний */
    backdrop-filter: blur(10px);    /* Розмиття фону */
}

.header .container {
    display: flex;
    justify-content: center;      /* Логотип по центру */
    align-items: center;
    position: relative;          /* Для absolute позиціонування nav-menu */
}

.header-logo {
    display: flex;
    justify-content: center;
    align-items: center;
}

.header-logo-img {
    height: 45px;
    width: auto;
    transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}
```

#### B) Навігаційне меню - Desktop (рядки 98-119)

```css
.nav-menu {
    position: absolute;           /* Відносно .header .container */
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);  /* Центрування відносно логотипу */
    display: flex;
    justify-content: space-between;    /* nav-left | logo | nav-right */
    align-items: center;
    width: 100%;
    max-width: 1300px;
    opacity: 0;                   /* Спочатку невидиме */
    visibility: hidden;
    transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    pointer-events: none;         /* Не блокує клікабельність логотипу */
    padding: 0 6rem;             /* Відступи з боків */
}

.nav-menu.active {
    opacity: 1;                   /* Показати меню */
    visibility: visible;
    pointer-events: auto;         /* Активувати кліки */
}
```

#### C) Ліва і права частини меню (рядки 121-135)

```css
.nav-left {
    display: flex;
    flex-direction: row;
    gap: 1.5rem;                 /* Відступи між кнопками */
    align-items: center;
    justify-content: flex-start;
}

.nav-right {
    display: flex;
    flex-direction: row;
    gap: 1.5rem;
    align-items: center;
    justify-content: flex-end;
}
```

#### D) Кнопки навігації (рядки 137-159)

```css
.nav-btn {
    background: transparent;
    border: none;
    color: #fff;
    font-family: 'Maison_Neue_Book', sans-serif;
    font-size: 0.9rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    cursor: pointer;
    transition: all 0.3s ease;
    opacity: 0;                   /* Спочатку невидимі для анімації */
    padding: 0.8rem 1rem;
    white-space: nowrap;
    flex-shrink: 0;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.nav-btn:hover {
    opacity: 0.7;                 /* Hover ефект */
}
```

#### E) Анімація появи кнопок (рядки 161-191)

```css
.nav-menu.active .nav-btn {
    animation: gentleBlink 1.2s ease both;  /* Ефект "блимання" */
}

/* Затримки для послідовної анімації */
.nav-menu.active .nav-left .nav-btn:nth-child(1) {
    animation-delay: 0.3s;        /* Membership */
}

.nav-menu.active .nav-left .nav-btn:nth-child(2) {
    animation-delay: 0.5s;        /* Contacts */
}

.nav-menu.active .nav-left .nav-btn:nth-child(3) {
    animation-delay: 0.7s;        /* My Account */
}

.nav-menu.active .nav-left .nav-btn:nth-child(4) {
    animation-delay: 0.9s;        /* Sign Up / Sign In */
}

.nav-menu.active .nav-right .nav-btn:nth-child(1) {
    animation-delay: 1.1s;        /* Mensuite */
}

.nav-menu.active .nav-right .nav-btn:nth-child(2) {
    animation-delay: 1.3s;        /* Coresync Private */
}

.nav-menu.active .nav-right .nav-btn:nth-child(3) {
    animation-delay: 1.5s;        /* BOOK NOW */
}
```

#### F) Кнопка "BOOK NOW" (рядки 193-212)

```css
.nav-btn--book {
    background: #F5F5DC;          /* Бежевий фон */
    border: 1px solid #F5F5DC;
    color: #000;                  /* Чорний текст */
    padding: 0.8rem 1.5rem;
    border-radius: 6px;
    font-family: 'Maison_Neue_Bold', sans-serif;
    font-size: 0.85rem;
    letter-spacing: 1px;
    transition: all 0.3s ease;
    box-shadow: 0 2px 10px rgba(245, 245, 220, 0.3);
    height: 44px;
}

.nav-btn--book:hover {
    background: #E6E6D4;          /* Темніший бежевий */
    border-color: #E6E6D4;
    transform: translateY(-2px);  /* Підняття при hover */
    box-shadow: 0 4px 15px rgba(245, 245, 220, 0.5);
}
```

#### G) Анімація "gentleBlink" (рядки 218-242)

```css
@keyframes gentleBlink {
    0% {
        opacity: 0;               /* Невидимий */
    }
    20% {
        opacity: 0.7;
    }
    40% {
        opacity: 0.2;             /* Мерехтіння */
    }
    60% {
        opacity: 0.8;
    }
    80% {
        opacity: 0.3;
    }
    100% {
        opacity: 1;               /* Повністю видимий */
    }
}
```

#### H) Бургер меню (рядки 67-96)

```css
.burger-menu {
    position: absolute;
    right: 0;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 10px;
    z-index: 1001;               /* Над nav-menu */
}

.burger-line {
    width: 30px;
    height: 2px;
    background: #fff;
    transition: all .3s ease;
    border-radius: 1px;
}

/* Трансформація в X при активації */
.burger-menu.active .burger-line:nth-child(1) {
    transform: rotate(45deg) translate(6px, 6px);
}

.burger-menu.active .burger-line:nth-child(2) {
    opacity: 0;                  /* Середня лінія зникає */
}

.burger-menu.active .burger-line:nth-child(3) {
    transform: rotate(-45deg) translate(6px, -6px);
}
```

#### I) Зменшення логотипу при відкритті меню (рядок 214-216)

```css
.header.menu-open .header-logo-img {
    height: 30px;                /* З 45px → 30px */
}
```

---

## ⚙️ 3. JAVASCRIPT ФУНКЦІОНАЛЬНІСТЬ

### Файл: `/coresync_backend/static/js/script.js` (рядки 1-115)

#### A) Ініціалізація елементів (рядки 5-11)

```javascript
document.addEventListener('DOMContentLoaded', function () {
    const burgerMenu = document.getElementById('burger-menu');
    const navMenu = document.getElementById('nav-menu');
    const header = document.querySelector('.header');
    const headerLogo = document.querySelector('.header-logo');
    const footerBtn = document.querySelector('.footer-btn');
    const heroImage = document.querySelector('.hero-image');
```

#### B) Функція toggle меню (рядки 41-59)

```javascript
function toggleMenu() {
    const isActive = navMenu.classList.contains('active');

    if (!isActive) {
        // Відкрити меню
        if (burgerMenu) burgerMenu.classList.add('active');  // X іконка
        header.classList.add('menu-open');                   // Зменшити логотип
        
        setTimeout(() => {
            navMenu.classList.add('active');                 // Показати меню з анімацією
        }, 200);
    } else {
        // Закрити меню
        if (burgerMenu) burgerMenu.classList.remove('active');
        navMenu.classList.remove('active');
        header.classList.remove('menu-open');
    }
}
```

#### C) Обробник кліку на бургер меню (рядки 61-66)

```javascript
if (burgerMenu && navMenu) {
    burgerMenu.addEventListener('click', function () {
        toggleMenu();
    });
}
```

#### D) Обробник кліку на логотип (мобільна версія) (рядки 68-78)

```javascript
if (headerLogo && navMenu) {
    headerLogo.addEventListener('click', function (e) {
        // Тільки на мобільних екранах
        if (window.innerWidth <= 768) {
            e.preventDefault();      // Не переходити на home
            toggleMenu();
        }
        // На desktop - нормальна поведінка посилання
    });
}
```

#### E) Навігація по кнопках меню (рядки 80-104)

```javascript
if (navMenu) {
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const link = this.getAttribute('data-link');
            if (link) {
                // Fade out меню
                navMenu.style.opacity = '0';

                // Закрити меню з анімацією
                setTimeout(() => {
                    if (burgerMenu) burgerMenu.classList.remove('active');
                    navMenu.classList.remove('active');
                    header.classList.remove('menu-open');
                    navMenu.style.opacity = '1';
                }, 400);

                // Навігація після анімації
                setTimeout(() => {
                    window.location.href = link;
                }, 800);
            }
        });
    });
}
```

---

## 📱 4. АДАПТИВНІ МЕДІА-ЗАПИТИ

### A) Планшети та мобільні (≤1024px) - рядки 644-720

```css
@media(max-width:1024px) {
    .nav-menu {
        display: none;           /* Спочатку приховано */
    }

    .nav-menu.active {
        display: flex;
        position: fixed;         /* Fullscreen оверлей */
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        width: 100vw;
        height: 100vh;
        flex-direction: column;  /* Вертикальне меню */
        transform: none;
        justify-content: center;
        align-items: center;
        background: rgba(0, 0, 0, 0.98);  /* Майже непрозорий */
        padding: 8rem 2rem 4rem 2rem;
        max-width: none;
        z-index: 998;
        overflow-y: auto;
        -webkit-overflow-scrolling: touch;
    }

    .nav-left,
    .nav-right {
        flex-direction: column;  /* Вертикально */
        width: 100%;
        max-width: 500px;
        gap: 0;
    }

    .nav-btn {
        width: 100%;
        justify-content: center;
        padding: 1.5rem 2rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        opacity: 1 !important;
        animation: none !important;  /* Без анімації на мобільних */
        min-height: 56px;
        font-size: 1.1rem;
        letter-spacing: 0.15em;
        visibility: visible !important;
        color: #fff !important;
    }

    .nav-btn:active {
        background: rgba(255, 255, 255, 0.1);  /* Feedback при кліку */
    }

    .nav-btn:first-child {
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
}
```

### B) Мобільні (≤768px) - рядки 757-783

```css
@media(max-width:768px) {
    .container {
        padding: 0 0rem;
    }

    /* Приховати бургер - логотип стає тригером */
    .burger-menu {
        display: none;
    }

    .header-logo {
        cursor: pointer;
        z-index: 1001;
        position: relative;
        transition: transform 0.3s ease;
    }

    .header-logo:active {
        transform: scale(0.95);  /* Візуальний feedback */
    }

    .nav-menu.active {
        padding: 7rem 1.5rem 3rem 1.5rem;
        justify-content: flex-start;
    }

    .nav-btn {
        font-size: 1rem;
        padding: 1.3rem 1.5rem;
    }
}
```

---

## 🎯 5. ПОВЕДІНКА МЕНЮ

### Desktop (>1024px):
1. **Закрите меню:**
   - Видимий тільки логотип по центру
   - Бургер меню (3 лінії) справа
   - Nav-menu невидиме (`opacity: 0`)

2. **Відкрите меню:**
   - Клік на бургер → `toggleMenu()`
   - Бургер трансформується в X
   - Логотип зменшується (45px → 30px)
   - Nav-menu з'являється з анімацією
   - Кнопки з'являються послідовно з ефектом "блимання"
   - Layout: `[nav-left] [LOGO] [nav-right]`

3. **Навігація:**
   - Клік на кнопку → fade out → перехід на сторінку

### Mobile (≤768px):
1. **Закрите меню:**
   - Видимий тільки логотип
   - Бургер приховано

2. **Відкрите меню:**
   - Клік на логотип → fullscreen оверлей
   - Вертикальне меню по центру
   - Чорний напівпрозорий фон
   - Кнопки на всю ширину з border

---

## 📊 6. ТАБЛИЦЯ ЕЛЕМЕНТІВ

| Елемент | Клас | Функція | Desktop | Mobile |
|---------|------|---------|---------|--------|
| Header контейнер | `.header` | Фіксований вгорі | Fixed top | Fixed top |
| Логотип | `.header-logo-img` | Центральний логотип | 45px → 30px (open) | Clickable trigger |
| Навігація | `.nav-menu` | Контейнер меню | Horizontal, hidden | Fullscreen overlay |
| Ліва частина | `.nav-left` | 3 кнопки зліва | Row, flex-start | Column, center |
| Права частина | `.nav-right` | 3 кнопки справа | Row, flex-end | Column, center |
| Кнопка меню | `.nav-btn` | Навігаційна кнопка | Transparent, uppercase | Full width, bordered |
| Book кнопка | `.nav-btn--book` | Спеціальна кнопка | Beige bg, shadow | Beige bg |
| Бургер | `.burger-menu` | Тригер меню | Видимий справа | Прихований |

---

## 🎨 7. КОЛІРНА СХЕМА

| Елемент | Колір | Опис |
|---------|-------|------|
| Header background | `rgba(0, 0, 0, 0.9)` | Напівпрозорий чорний |
| Nav buttons | `#fff` | Білий текст |
| Nav buttons hover | `opacity: 0.7` | Напівпрозорий |
| Book button bg | `#F5F5DC` | Бежевий |
| Book button hover | `#E6E6D4` | Темніший бежевий |
| Book button text | `#000` | Чорний |
| Burger lines | `#fff` | Білі лінії |
| Mobile overlay | `rgba(0, 0, 0, 0.98)` | Майже чорний |

---

## ⏱️ 8. ТАЙМИНГИ АНІМАЦІЙ

| Анімація | Тривалість | Затримка | Ефект |
|----------|------------|----------|-------|
| Nav menu появa | 0.6s | 0.2s | Cubic-bezier ease |
| Кнопка 1 (Membership) | 1.2s | 0.3s | gentleBlink |
| Кнопка 2 (Contacts) | 1.2s | 0.5s | gentleBlink |
| Кнопка 3 (My Account) | 1.2s | 0.7s | gentleBlink |
| Кнопка 4 (Sign Up) | 1.2s | 0.9s | gentleBlink |
| Кнопка 5 (Mensuite) | 1.2s | 1.1s | gentleBlink |
| Кнопка 6 (Private) | 1.2s | 1.3s | gentleBlink |
| Кнопка 7 (Book Now) | 1.2s | 1.5s | gentleBlink |
| Fade out при кліку | - | 0.4s | Opacity → 0 |
| Навігація | - | 0.8s | Location change |
| Book hover | 0.3s | - | Transform + shadow |

---

## 🔑 9. КЛЮЧОВІ ОСОБЛИВОСТІ

### ✅ Desktop меню:
- Логотип завжди по центру
- Кнопки з'являються з обох боків при відкритті
- Ефект "блимання" для плавної появи
- Book Now має особливий дизайн (бежевий фон)
- Бургер трансформується в X

### ✅ Smooth transitions:
- Cubic-bezier для плавності
- Послідовна анімація кнопок (0.3s - 1.5s затримка)
- Fade out при навігації
- Hover ефекти на всіх інтерактивних елементах

### ✅ Responsive:
- >1024px: Horizontal layout
- ≤1024px: Fullscreen overlay
- ≤768px: Logo as menu trigger
- Touch-friendly на мобільних

### ✅ Accessibility:
- Клавіатурна навігація (button elements)
- Smooth scroll на iOS
- Touch feedback (scale/opacity)
- Aria-friendly structure

---

## 📁 10. ФАЙЛИ

| Файл | Призначення | Рядки |
|------|-------------|-------|
| `templates/base.html` | HTML структура | 17-51 |
| `static/css/styles.css` | Базові стилі | 37-242 |
| `static/css/styles.css` | Адаптивні стилі | 644-783 |
| `static/js/script.js` | Функціональність | 1-115 |

---

## ✅ ПЕРЕВІРЕНИЙ ФУНКЦІОНАЛ

- ✅ Відкриття/закриття меню
- ✅ Навігація по кнопках
- ✅ Анімація появи кнопок
- ✅ Трансформація бургера в X
- ✅ Зменшення логотипу при відкритті
- ✅ Hover ефекти
- ✅ Адаптивність для планшетів
- ✅ Адаптивність для мобільних
- ✅ Логотип як тригер на мобільних
- ✅ Touch-friendly інтерфейс
- ✅ Smooth transitions
- ✅ iOS оптимізація

---

**Автор:** AI Assistant  
**Дата:** 7 жовтня 2025

