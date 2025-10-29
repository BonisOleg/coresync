"""
Technicians App Configuration.
"""
from django.apps import AppConfig


class TechniciansConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'technicians'
    verbose_name = 'Technician Portal'
    
    def ready(self):
        """Import signals."""
        try:
            import technicians.signals  # noqa
        except ImportError:
            pass
