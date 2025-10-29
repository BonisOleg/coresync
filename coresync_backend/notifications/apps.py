"""
Notifications App Configuration.
"""
from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
    verbose_name = 'Email Notifications'
    
    def ready(self):
        """Import signals."""
        try:
            import notifications.signals  # noqa
        except ImportError:
            pass
