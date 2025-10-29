# Django configuration package

# Import Celery app for autodiscovery (після встановлення залежностей)
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    # Celery not installed yet - will be enabled after pip install
    pass
