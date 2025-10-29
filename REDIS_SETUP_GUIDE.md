# Redis Setup Guide для Render.com

## Крок 1: Додати Redis Addon в Render Dashboard

1. Відкрийте Render.com dashboard
2. Натисніть на ваш CoreSync service
3. Environment → Add Database → Redis
4. Виберіть Free tier (25MB) або Starter ($10/міс, 256MB)
5. Render автоматично створить `REDIS_URL` environment variable

## Крок 2: Environment Variables

Додайте у Render.com Environment panel:

```bash
# Redis Configuration
REDIS_URL=<автоматично створюється Render>
CELERY_BROKER_URL=${REDIS_URL}/1
CELERY_RESULT_BACKEND=${REDIS_URL}/2

# Email Configuration
SENDGRID_API_KEY=<отримати від client>

# Atlas AI Configuration (BLOCKED - чекаємо)
ATLAS_API_KEY=<буде пізніше>
ATLAS_WEBHOOK_SECRET=<буде пізніше>
ATLAS_BASE_URL=https://api.youratlas.com/v1

# Google Services (BLOCKED - потребує payment card)
GOOGLE_CALENDAR_SERVICE_ACCOUNT_FILE=/path/to/service-account.json
GOOGLE_SHEETS_SERVICE_ACCOUNT_FILE=/path/to/service-account.json

# Monitoring
SENTRY_DSN=<optional>
```

## Крок 3: Додати Celery Worker Service

В Render.com створити **Background Worker**:

### Worker 1: Default Queue
- Name: `coresync-celery-worker`
- Environment: Same as Web Service
- Start Command: `celery -A config worker -l info -Q default,emails,payments`
- Instance Type: Starter ($7/міс) або Free

### Worker 2 (Optional): AI Queue
- Name: `coresync-celery-ai-worker`
- Start Command: `celery -A config worker -l info -Q ai --concurrency=4`
- Instance Type: Starter (для multithreading)

## Крок 4: Додати Celery Beat Scheduler

Створити ще один Background Worker:

- Name: `coresync-celery-beat`
- Environment: Same as Web Service
- Start Command: `celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler`
- Instance Type: Free (не потребує багато ресурсів)

## Крок 5: Тестування Локально

```bash
# Terminal 1: Django server
cd coresync_backend
python3 manage.py runserver

# Terminal 2: Celery worker
celery -A config worker -l info

# Terminal 3: Celery beat
celery -A config beat -l info

# Terminal 4: Flower monitoring (optional)
celery -A config flower
```

Відкрийте http://localhost:5555 для Flower dashboard.

## Крок 6: Міграції

```bash
python3 manage.py migrate django_celery_beat
```

## Статус Блокерів

❌ **Google Cloud APIs** - потребує payment card від client  
❌ **Atlas AI** - потребує subscription activation  
✅ **Redis** - можна налаштувати зараз  
✅ **Celery Infrastructure** - готово до deploy  
⏳ **QuickBooks** - credentials в November  

## Next Steps

1. ✅ Requirements.txt оновлено
2. ✅ config/celery.py створено
3. ✅ settings.py налаштовано
4. ⏳ Redis addon на Render (client action)
5. ⏳ Celery workers deploy (після Redis)
6. → Переходимо до Day 3: AI Agent App створення

