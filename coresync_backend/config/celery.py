"""
Celery configuration for CoreSync project.
Async task processing for bookings, emails, QuickBooks sync.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('coresync')

# Load configuration from Django settings with 'CELERY_' prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# Celery Beat Schedule (Cron Tasks)
app.conf.beat_schedule = {
    # Daily reminders at 9 AM EST
    'send-daily-reminders': {
        'task': 'notifications.tasks.send_daily_reminders_batch',
        'schedule': crontab(hour=9, minute=0),
    },
    
    # Hourly QuickBooks sync
    'hourly-quickbooks-sync': {
        'task': 'payments.tasks.hourly_qb_sync',
        'schedule': crontab(minute=0),  # Every hour
    },
    
    # Nightly reconciliation at 2 AM EST
    'nightly-reconcile': {
        'task': 'payments.tasks.reconcile_stripe_qb',
        'schedule': crontab(hour=2, minute=0),
    },
    
    # Weekly payroll export Thursday 6 PM EST
    'weekly-payroll-export': {
        'task': 'technicians.tasks.export_weekly_payroll',
        'schedule': crontab(day_of_week=4, hour=18, minute=0),
    },
    
    # Daily session cleanup at 3 AM EST
    'daily-session-cleanup': {
        'task': 'ai_agent.tasks.cleanup_old_conversations',
        'schedule': crontab(hour=3, minute=0),
    },
    
    # Daily analytics export at 4 AM EST
    'daily-analytics-export': {
        'task': 'analytics.tasks.export_to_sheets',
        'schedule': crontab(hour=4, minute=0),
    },
}

# Task settings
app.conf.task_routes = {
    'ai_agent.*': {'queue': 'ai'},
    'notifications.*': {'queue': 'emails'},
    'payments.*': {'queue': 'payments'},
    'technicians.*': {'queue': 'default'},
}

app.conf.task_default_queue = 'default'
app.conf.task_default_exchange = 'default'
app.conf.task_default_routing_key = 'default'

# Result backend settings
app.conf.result_expires = 3600  # 1 hour

# Timezone
app.conf.timezone = 'America/New_York'

@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup."""
    print(f'Request: {self.request!r}')

