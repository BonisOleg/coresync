"""
Technicians Django Signals - Auto-sync triggers.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

from .models import WorkLog, Schedule

logger = logging.getLogger(__name__)


@receiver(post_save, sender=WorkLog)
def worklog_saved(sender, instance, created, **kwargs):
    """
    Trigger Google Sheets sync після WorkLog save.
    
    Only sync якщо approved=True.
    """
    if instance.approved and not instance.synced_to_sheets:
        try:
            # Queue async task
            from .tasks import sync_worklog_to_sheets
            sync_worklog_to_sheets.delay(instance.id)
            
            logger.info(f"Queued sync for worklog {instance.id}")
        except ImportError:
            # Celery not available
            logger.warning("Celery not configured, sync not queued")
        except Exception as e:
            logger.error(f"Error queueing worklog sync: {str(e)}")


@receiver(post_save, sender=Schedule)
def schedule_saved(sender, instance, created, **kwargs):
    """
    Trigger availability update після Schedule change.
    """
    try:
        from .tasks import update_technician_availability
        update_technician_availability.delay(instance.technician.id)
        
        logger.info(f"Queued availability update for technician {instance.technician.id}")
    except ImportError:
        logger.warning("Celery not configured, availability update not queued")
    except Exception as e:
        logger.error(f"Error queueing availability update: {str(e)}")

