# CoreSync App - Досвід Користувача (UX Vision)

## 📱 Клієнтський Досвід

### 1. Вхід та Аутентифікація
- **Завантаження:** App Store/Google Play (безкоштовно)
- **Доступ:** Тільки члени можуть увійти
- **Не-члени:** Екран реєстрації з планами (Mensuite, Coresync Private, Unlimited)
- **Перший вхід:** Обов'язкове збереження кредитної картки

### 2. Головна Панель
**Вітання:** "Welcome back, [Ім'я]"

**Основні Портали:**
- 🔸 Mensuite (Men's Spa)
- 🔸 Coresync Private (Couple's Spa)

**Швидкі Кнопки:**
- Book a Service
- Reserve Backyard
- Meditation Pod
- Shop Spa Products
- My Membership & Benefits

### 3. Бронювання Послуг
- **Календар:** Реал-тайм доступність
- **Пріоритет:** Автоматично для членів
- **Оплата:** One-tap (з збереженої картки)
- **Pre-Select Options:**
  - AI massage bed program
  - Facial add-ons
  - Lighting/mood scenes

### 4. AI Персоналізація
- **Останні послуги + дати**
- **Рекомендації:** "We suggest Light Therapy + Oxygen Dome this week"
- **Частота бронювання**
- **Пропозиції апгрейдів**

### 5. Медитаційні Поди
- **AI-guided breathwork** сесії
- **Керування:** Start, style selection, sleep/relax programs
- **Збереження преференцій**
- **Регулярні сесії**

### 6. Кастомізація Середовища
- **Coresync Private:** Immersive screen scenes (Swiss Alps, Venice, ocean)
- **Персональні плейлисти**
- **Власні візуали**

### 7. Спа Магазин + Консьєрж
- **Retail Items:** Skincare, wellness tech, accessories
- **Доставка:** Готові до наступного візиту (не shipping)
- **Консьєрж Запити:**
  - Спеціальні замовлення (whisky, flowers, luxury accessories)
  - Лінк + опис + бюджет
  - One-tap charging

### 8. Членство та Винагороди
- **Рівні:** Mensuite, Private, Unlimited
- **Переваги:** Priority booking, unlimited access, exclusive perks
- **День народження:** "Choose your free service"

### 9. Інвестиційні Можливості
- **Приватна вкладка "Investor"**
- **Інформація про інвестиції в Coresync**

---

## 🛠️ Адміністраторський Досвід

### 1. Головна Панель
- **Реал-тайм бронювання** (Mensuite & Private)
- **Активні кімнати** та обладнання
- **Meditation pods** статус

### 2. Профілі Членів
- **Історія послуг**
- **AI рекомендації**
- **Преференції налаштувань**
- **Використані переваги**

### 3. Бронювання та Платежі
- **Card-on-file** система
- **Денні/тижневі доходи**
- **Membership upgrades**
- **Retail purchases**
- **Comp/gift services** (VIPs, birthdays)

### 4. Керування Обладнанням
- **Meditation pods** sync
- **Immersive screens** playlists
- **AI massage bed** programs

### 5. Інвентар та Магазин
- **Product catalog** (instant app updates)
- **Retail sales** tracking
- **Concierge requests** управління

### 6. Маркетинг
- **Push notifications:**
  - New service alerts
  - AI reminders
- **Таргетинг** по рівню членства

### 7. Інвестиційна Панель
- **Документи для інвесторів**
- **Запрошення та можливості**

---

## 📋 Ключові Сценарії

### Сценарій 1: David (Unlimited Member)
1. **Вхід:** "Welcome back, David"
2. **Вибір:** Mensuite → "Facial + Light Therapy" (Friday 3 PM)
3. **AI:** "Last time Oxygen Dome. Recommend combining again"
4. **Консьєрж:** Japanese whisky ($200 budget)
5. **Візит:** Face recognition → auto preferences → готові покупки
6. **Результат:** Auto charging + AI рекомендації на наступний раз

### Сценарій 2: Sarah & Eli (Coresync Private)
1. **Бронювання:** Saturday 7 PM private session
2. **Кастомізація:** Venice Canals scene + AI Massage + roses/champagne
3. **Візит:** Face recognition → готова suite з Venice visuals
4. **Досвід:** Hot tub + AI massage + guided breathwork
5. **Результат:** Auto charging + AI рекомендації (Oxygen Dome)

---

## ❓ Додаткові Питання до Клієнта

### Технічні Деталі
1. **Список обладнання для інтеграції:** AI massage bed, meditation pod, oxygen dome, LED light therapy, immersive screens
2. **Назви кімнат:** Для правильного labeling в додатку
3. **Face recognition система:** Який провайдер/технологія?
4. **Card-on-file:** Stripe Customer Portal чи окрема інтеграція?

### Функціональні Питання
5. **Інвестиційна вкладка:** Які документи, хто має доступ?
6. **Консьєрж бюджети:** Максимальні ліміти, схвалення?
7. **AI рекомендації:** Яка логіка, дані для навчання?
8. **Priority booking:** Скільки днів наперед для членів?

### Бізнес Логіка
9. **Membership перехід:** Можна апгрейднути через додаток?
10. **Retail доставка:** Як довго зберігати товари?
11. **Backyard резервація:** Окремо від основних послуг?
12. **Birthday perks:** Один раз на рік, які послуги доступні?

### UX/UI Деталі
13. **Immersive scenes:** Власна бібліотека чи сторонні контент?
14. **Personal playlists:** Spotify/Apple Music інтеграція?
15. **Push notifications:** Частота, типи, opt-out?
16. **Offline функціональність:** Що доступно без інтернету?

---

## 🔄 Оновлення Архітектури

### Нові Моделі (Додати до існуючих):
- **Equipment** - AI massage beds, meditation pods, oxygen domes
- **Scenes** - Immersive screen content library
- **ConciergeRequest** - Custom orders з бюджетом
- **Notification** - Push notifications management
- **Investment** - Investor documents та opportunities

### Нові API Endpoints:
- `/api/equipment/` - Керування обладнанням
- `/api/scenes/` - Immersive scenes library
- `/api/concierge/` - Custom requests
- `/api/ai/recommendations/` - AI suggestions
- `/api/notifications/` - Push notifications

### Інтеграції:
- **Face Recognition API**
- **Stripe Customer Portal** (advanced)
- **Content Delivery** для immersive scenes
- **AI/ML Service** для рекомендацій
