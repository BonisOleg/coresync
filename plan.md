# ПЛАН ПРОЕКТУ CORESYNC WEBSITE & MOBILE APP

## 📋 ЗАГАЛЬНА ІНФОРМАЦІЯ

### Проект
- **Назва:** CoreSync Website & Mobile App
- **Тип:** Спа-центр з IoT інтеграцією
- **Клієнт:** C. STERN (+1 (347) 899-5612)
- **Команда:** PrometeyLabs
- **Ціна:** $5,900
- **Депозит:** $3,000 (отримано через PayPal)

### Таймлайн
- **18 вересня 2024:** Базова версія
- **15 жовтня 2024:** Завершена версія
- **1 листопада 2024:** Фінальне тестування
- **Щотижневі звіти:** Кожен четвер з скріншотами

### Технологічний стек
- **Backend:** Django (спільний для сайту та додатку)
- **Frontend:** HTML/CSS/Vanilla JavaScript
- **Mobile:** Flutter (iOS + Android)
- **Платежі:** Stripe (Payment Sheet + Apple Pay/Google Pay)
- **Бухгалтерія:** QuickBooks API
- **Домен:** GoDaddy
- **Email:** info@coresync.life, hindy@cstern.info

---

## 🏗️ АРХІТЕКТУРА СИСТЕМИ

### Системна схема
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flutter App   │    │   HTML/CSS/JS   │    │   IoT Gateway   │
│   (iOS/Android) │    │   (Website)     │    │   (Spa Control) │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │      Django Backend       │
                    │   (API + Business Logic)  │
                    └─────────────┬─────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
┌─────────▼─────────┐  ┌─────────▼─────────┐  ┌─────────▼─────────┐
│   QuickBooks API  │  │   Stripe API      │  │   GA4 Analytics   │
│   (Payments/Inv)  │  │   (Payments)      │  │   (Tracking)      │
└───────────────────┘  └───────────────────┘  └───────────────────┘
```

### База даних (Django Models)
```python
# Core models
User (Member/Non-Member)
Service (Mensuite/Coresync Private)
Pricing (Member/Non-Member prices)
Membership (Plans & Benefits)
Booking (Phase 2)
Payment (Stripe integration)
IoTDevice (Spa equipment control)
UserPreference (Scenes, scents, lighting)
ServiceHistory
```

---

## 🌐 ВЕБ-САЙТ (HTML/CSS/Vanilla JavaScript)

### Структура сайту

#### 1. Головна сторінка (Home)
- **Hero секція:**
  - Hero image/video (сучасний дизайн спа + технології)
  - Короткий опис Mensuite (чоловічий спа)
  - Короткий опис Coresync Private (парний спа)
  - CTA кнопки: "Book Now" + "Join Membership"

#### 2. Mensuite - Men's Spa
- **Повний список послуг з цінами**
- **Таблиці цін:** Member vs Non-Member (для заохочення членства)
- **Технологічні особливості:**
  - Smart Mirror
  - AI Analyzer
- **Медитаційна кімната**
- **Фото:** барберські послуги, лазерні процедури, AI масаж

#### 3. Coresync Private - Couple Spa
- **AI Suite огляд:** масажні ліжка, сауна, джакузі
- **Приватний зовнішній hot tub**
- **Таблиці цін:** Member vs Non-Member
- **Фото/відео:** повний досвід для пар

#### 4. Членство (Membership)
- **Назви планів членства**
- **Конкретні бенефіти**
- **Приклад економії**
- **Форма реєстрації** (email: @+1 (347) 899-5612)

#### 5. Технології та Інновації
- **Список пристроїв/технологій** з короткими описам
- **Медіа посилання**

#### 6. Про нас/Кар'єра
- **Коротка історія бренду**
- **Візія**
- **Відкриті позиції** та email для заявок

#### 7. Контакти
- **Точна адреса** для карти
- **Телефон** (основний + WhatsApp)
- **Робочі години:** 12hr формат
- **Святковий графік**
- **Соціальні мережі:** Instagram, Facebook

#### 8. Форми
- **Contact Form:** Name, Email, Phone, Message
- **Join Membership Form**
- **reCAPTCHA** (так/ні)
- **Цільові email адреси** (окремі для кожної форми)

### Технічні вимоги сайту
- **SEO оптимізація**
- **Мова:** Англійська (за замовчуванням)
- **Meta descriptions** та page titles
- **GA4 інтеграція** (Measurement ID: створити під info@coresync.life)
- **Staging environment** з basic auth
- **Production environment**
- **Domain:** GoDaddy (потрібен доступ)

---

## 📱 МОБІЛЬНИЙ ДОДАТОК (Flutter)

### Основна функціональність

#### 1. Аутентифікація
- **Email/Apple/Google sign-in**
- **Face recognition** (якщо технічно можливо)
- **Device biometrics** (fallback)

#### 2. Контроль спа-середовища (IoT)
- **Створення сцен:** користувачі можуть створювати власні сцени на екрані в спа
- **Контроль ароматів:** налаштування запахів через додаток
- **Освітлення:** регулювання типу освітлення в спа
- **Температура:** контроль температури (логічно випливає)
- **Real-time синхронізація** з фізичним середовищем

#### 3. Персоналізація
- **Налаштування сцен**
- **Налаштування ароматів**
- **Налаштування освітлення**
- **Збереження преференцій**

#### 4. Історія та рекомендації
- **Перегляд послуг**
- **Історія обслуговування**
- **Автоматичні нагадування** про наступні послуги
- **Налаштування преференцій**

#### 5. Безконтактні операції
- **Face recognition/fingerprint** для add-ons
- **Покупки без checkout** (через біометрію)
- **Автоматичні платежі** за додаткові послуги

#### 6. Контент (Read-only)
- **Список послуг**
- **Інформація про членство**
- **Контактна інформація**

### Технічні вимоги додатку
- **iOS** (App Store)
- **Android** (Google Play)
- **IoT API інтеграція**
- **Real-time комунікація**
- **Безпека** для контролю критичних систем
- **Offline функціональність** (базовий контент)

---

## 🔧 BACKEND (Django)

### API Endpoints

#### Аутентифікація
```
POST /api/auth/login/
POST /api/auth/register/
POST /api/auth/logout/
POST /api/auth/refresh/
```

#### Користувачі
```
GET /api/users/profile/
PUT /api/users/profile/
GET /api/users/preferences/
PUT /api/users/preferences/
```

#### Послуги
```
GET /api/services/
GET /api/services/{id}/
GET /api/services/mensuite/
GET /api/services/coresync-private/
```

#### Членство
```
GET /api/membership/plans/
POST /api/membership/join/
GET /api/membership/benefits/
```

#### IoT Контроль
```
POST /api/iot/scene/create/
PUT /api/iot/scene/{id}/
POST /api/iot/lighting/adjust/
POST /api/iot/scent/adjust/
POST /api/iot/temperature/set/
GET /api/iot/status/
```

#### Історія
```
GET /api/history/services/
GET /api/history/bookings/
POST /api/history/recommendations/
```

#### Форми
```
POST /api/forms/contact/
POST /api/forms/membership/
```

### Інтеграції

#### QuickBooks API
- **Синхронізація платежів**
- **Синхронізація замовлень**
- **Синхронізація інвентарю**
- **Автоматичне оновлення** даних

#### Stripe API
- **Payment Sheet**
- **Apple Pay/Google Pay**
- **Device biometrics**
- **Автоматичні платежі** за add-ons

#### IoT Gateway
- **REST API** для контролю обладнання
- **WebSocket** для real-time комунікації
- **Безпека** та авторизація
- **Логування** всіх операцій

---

## 📊 БАЗА ДАНИХ

### Основні таблиці

#### Users
```sql
- id (Primary Key)
- email
- first_name
- last_name
- phone
- membership_status (Member/Non-Member)
- membership_plan_id (FK)
- face_recognition_data (encrypted)
- created_at
- updated_at
```

#### Services
```sql
- id (Primary Key)
- name
- description
- category (Mensuite/Coresync Private)
- duration
- member_price
- non_member_price
- is_active
- created_at
```

#### MembershipPlans
```sql
- id (Primary Key)
- name
- description
- benefits (JSON)
- price
- duration_months
- is_active
```

#### UserPreferences
```sql
- id (Primary Key)
- user_id (FK)
- scene_name
- scene_config (JSON)
- scent_preferences (JSON)
- lighting_preferences (JSON)
- temperature_preferences (JSON)
- created_at
```

#### ServiceHistory
```sql
- id (Primary Key)
- user_id (FK)
- service_id (FK)
- booking_date
- completion_date
- notes
- created_at
```

#### IoTDevices
```sql
- id (Primary Key)
- device_type (lighting/scent/temperature)
- device_name
- device_location
- current_status (JSON)
- last_updated
```

---

## 🔐 БЕЗПЕКА

### Аутентифікація
- **JWT токени**
- **Refresh tokens**
- **Face recognition** (якщо можливо)
- **Device biometrics** (fallback)

### Авторизація
- **Role-based access** (Member/Non-Member/Admin)
- **API rate limiting**
- **CORS налаштування**

### IoT Безпека
- **API ключі** для IoT пристроїв
- **Шифрування** комунікації
- **Логування** всіх операцій
- **Валідація** команд

### Дані
- **Шифрування** особистих даних
- **GDPR compliance**
- **Політика видалення** даних (12/24 місяці)
- **Backup стратегія**

---

## 🚀 ЕТАПИ РОЗРОБКИ

### Етап 1: Архітектура та планування (Тиждень 1)
- [ ] Створення проектної структури
- [ ] Налаштування Django проекту
- [ ] Створення Flutter проекту
- [ ] Визначення API endpoints
- [ ] Планування бази даних
- [ ] Налаштування середовищ (staging/production)

### Етап 2: Backend розробка (Тижні 2-4)
- [ ] Django models та міграції
- [ ] API endpoints
- [ ] Аутентифікація та авторизація
- [ ] QuickBooks інтеграція
- [ ] Stripe інтеграція
- [ ] IoT API структура

### Етап 3: Frontend розробка (Тижні 3-5)
- [ ] HTML структура
- [ ] CSS стилізація
- [ ] JavaScript функціональність
- [ ] Форми та валідація
- [ ] SEO оптимізація
- [ ] GA4 інтеграція

### Етап 4: Flutter додаток (Тижні 4-7)
- [ ] Базова структура
- [ ] Аутентифікація
- [ ] API клієнт
- [ ] IoT контроль
- [ ] Персоналізація
- [ ] Історія та рекомендації

### Етап 5: Інтеграція та тестування (Тижні 6-8)
- [ ] End-to-end тестування
- [ ] IoT інтеграція
- [ ] Платіжні тести
- [ ] Безпека тестування
- [ ] Performance оптимізація

### Етап 6: Запуск (Тиждень 9)
- [ ] Production deployment
- [ ] Domain налаштування
- [ ] SSL сертифікати
- [ ] Monitoring налаштування
- [ ] Фінальне тестування

---

## 📋 ЧЕКАЄМО ВІД КЛІЄНТА

### Дизайн та брендинг
- [ ] Логотип (SVG/PNG)
- [ ] Фірмові кольори
- [ ] Фірмові шрифти
- [ ] 1-3 референсні веб-сайти
- [ ] Hero фото/відео для головної сторінки

### Контент
- [ ] Фінальний список послуг (Mensuite + Coresync Private)
- [ ] Ціни Member vs Non-Member для кожної послуги
- [ ] Назви планів членства та конкретні бенефіти
- [ ] Коротка історія бренду та візія
- [ ] Точна адреса для карти
- [ ] Робочі години та святковий графік
- [ ] Instagram та Facebook посилання

### Технічні деталі
- [ ] Домен/DNS доступ (GoDaddy)
- [ ] Цільові email адреси для форм
- [ ] Privacy Policy, Terms of Service, Refund/Cancellation
- [ ] Показувати тривалість послуг (так/ні)
- [ ] Add-ons для послуг
- [ ] GA4 owner email підтвердження

### IoT обладнання
- [ ] Специфікації IoT пристроїв
- [ ] API документація для контролю обладнання
- [ ] Протоколи комунікації
- [ ] Безпека IoT систем

---

## 🎯 MVP SCOPE

### Phase 1 (Поточна фаза)
- ✅ Маркетинговий веб-сайт
- ✅ Read-only мобільний додаток
- ✅ IoT контроль для членів
- ✅ Форми контактів та членства
- ✅ QuickBooks інтеграція
- ✅ Stripe платежі

### Phase 2 (Після відкриття спа)
- ⏳ Внутрішнє бронювання
- ⏳ In-app платежі
- ⏳ Повна система управління

---

## 📞 КОНТАКТИ

### Команда клієнта
- **C. STERN:** +1 (347) 899-5612 (основний контакт)
- **Yossi Seidenfeld:** +1 (929) 314-6271 (технічний директор)
- **CSTERN:** +1 (917) 507-4015 (фінансовий директор)
- **Malky:** +1 (917) 733-8825 (дизайн)

### Email адреси
- **GA4:** info@coresync.life
- **Admin:** hindy@cstern.info
- **Команда розробки:** PrometeyLabs@gmail.com

---

## 🔄 ЩОТИЖНЕВІ ЗВІТИ

### Формат звіту (кожен четвер)
- [ ] Що було завершено за тиждень
- [ ] Скріншоти прогресу
- [ ] Технічні виклики
- [ ] Наступні кроки
- [ ] Питання до клієнта

### Критерії успіху
- [ ] Базова версія готова до 18 вересня
- [ ] Завершена версія готова до 15 жовтня
- [ ] Фінальне тестування завершено до 1 листопада
- [ ] Всі функції працюють стабільно
- [ ] Безпека перевірена
- [ ] Performance оптимізовано

---

## 📝 ДОДАТКОВІ ВИМОГИ ТА УТОЧНЕННЯ

### "Book Now" функціональність
- **НЕ WhatsApp** (як спочатку планувалося)
- **НЕ телефонний дзвінок**
- **АБО** AI чат для бронювання
- **АБО** пряме бронювання на сайті
- **Уточнити:** який варіант обирає клієнт

### AI функціональність
- **AI чат** для бронювання
- **AI відповідач** на телефоні (згадувалося в чаті)
- **AI рекомендації** для членів
- **AI аналіз** для персоналізації

### Біометрія та безпека
- **Face recognition** бажано, але не обов'язково
- **Device biometrics** (fallback)
- **Безконтактні покупки** через біометрію
- **Автоматичні платежі** за add-ons

### IoT інтеграція деталі
- **Real-time контроль** спа-середовища
- **Синхронізація** між додатком та фізичним середовищем
- **API для IoT пристроїв** (потрібна документація від клієнта)
- **Безпека IoT систем**

### Технічні уточнення
- **Мова:** Англійська (за замовчуванням)
- **Формат годин:** 12hr (підтверджено клієнтом)
- **Домен:** GoDaddy (потрібен доступ)
- **Email адреси:** info@coresync.life, hindy@cstern.info

### Чекаємо уточнення
- [ ] Який варіант "Book Now" обирає клієнт?
- [ ] Специфікації IoT обладнання
- [ ] API документація для IoT контролю
- [ ] Фінальні ціни послуг
- [ ] Деталі членства
- [ ] AI платформа для чату/відповідача
