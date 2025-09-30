# 🐛 RENDER DEPLOYMENT DEBUG GUIDE

## ❌ ПРОБЛЕМА: Деплой не запускається на Render

### 🔍 МОЖЛИВІ ПРИЧИНИ:

1. **Health Check Endpoint** 
   - `render.yaml` має `healthCheckPath: /health/`
   - Перевір чи доступний `/health/` endpoint

2. **Dependencies Conflicts**
   - QuickBooks залежності можуть конфліктувати
   - Celery/Redis не доступні на free tier

3. **Database Migrations**
   - Нові booking models потребують міграцій
   - PostgreSQL підключення

4. **Build Script Errors**
   - Python 3.13 сумісність
   - Права доступу до файлів

---

## 🚀 ШВИДКЕ ВИПРАВЛЕННЯ:

### Крок 1: Використай Спрощений Config
```bash
# Переіменуй файли:
mv render.yaml render_full.yaml
mv render_simple.yaml render.yaml

# Деплой з мінімальними залежностями
git add render.yaml
git commit -m "Deploy: simplified config for debug"
git push
```

### Крок 2: Перевір Logs на Render
1. Йди в Render Dashboard
2. Клікни на свій сервіс
3. Дивися "Build Logs" і "Deploy Logs"
4. Шукай помилки

### Крок 3: Поетапне Додавання
1. **Спочатку** - базовий Django
2. **Потім** - додай QuickBooks
3. **Останнім** - Celery/Redis

---

## 🔧 НАЛАШТУВАННЯ ДЛЯ RENDER:

### Environment Variables (обов'язково):
```
DEBUG=false
DJANGO_SETTINGS_MODULE=config.settings
SECRET_KEY=[auto-generated]
DATABASE_URL=[from postgres service]
ALLOWED_HOSTS=coresync.onrender.com,*.onrender.com
```

### Команди для Debug:
```bash
# Локальний тест
cd coresync_backend
python manage.py check --deploy

# Тест міграцій
python manage.py makemigrations --dry-run
python manage.py migrate --plan

# Тест static files
python manage.py collectstatic --dry-run
```

---

## 🎯 PRIORITY FIX STEPS:

1. **✅ ВИПРАВЛЕНО:** Health check endpoint `/health/`
2. **✅ ВИПРАВЛЕНО:** Спрощені залежності
3. **✅ ВИПРАВЛЕНО:** Fallback для QuickBooks
4. **🔄 ТЕСТУЙ:** Використовуй `render_simple.yaml`

---

## 📞 ЯКЩО ВСЕ ЩЕ НЕ ПРАЦЮЄ:

1. Перевір Render Dashboard logs
2. Використай `render_simple.yaml` 
3. Поступово додавай функції
4. Контактуй Render Support якщо проблема з платформою

**🚨 ГОЛОВНЕ: Спочатку запусти базову версію, потім додавай складність!**
