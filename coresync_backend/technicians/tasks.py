"""
Technicians Celery Tasks - Async operations.
"""
from celery import shared_task
import logging
from datetime import datetime, timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name='technicians.tasks.sync_worklog_to_sheets')
def sync_worklog_to_sheets(worklog_id: int):
    """
    Sync work log до Google Sheets асинхронно.
    Trigger: WorkLog.save() signal.
    """
    try:
        from .sheets_manager import technician_sheets_manager
        
        result = technician_sheets_manager.sync_worklog(worklog_id)
        
        logger.info(f"WorkLog {worklog_id} sync result: {result}")
        return {'status': 'success' if result else 'failed', 'worklog_id': worklog_id}
    
    except Exception as e:
        logger.error(f"Sync worklog task error: {str(e)}")
        raise


@shared_task(name='technicians.tasks.batch_sync_weekly_hours')
def batch_sync_weekly_hours():
    """
    Batch sync weekly hours (runs weekly).
    Celery beat: Thursday 6 PM EST.
    """
    try:
        from .sheets_manager import technician_sheets_manager
        
        # Current week
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        count = technician_sheets_manager.batch_sync_worklogs(week_start, week_end)
        
        logger.info(f"Weekly batch sync: {count} worklogs")
        return {'status': 'success', 'count': count}
    
    except Exception as e:
        logger.error(f"Batch sync weekly hours error: {str(e)}")
        raise


@shared_task(name='technicians.tasks.export_weekly_payroll')
def export_weekly_payroll():
    """
    Export weekly payroll CSV.
    Trigger: Celery beat Thursday 6 PM EST.
    """
    try:
        from .sheets_manager import technician_sheets_manager
        
        # Previous week
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday() + 7)
        week_end = week_start + timedelta(days=6)
        
        csv_path = technician_sheets_manager.export_payroll_csv(week_start, week_end)
        
        if csv_path:
            # TODO: Email до manager
            logger.info(f"Payroll exported: {csv_path}")
            return {'status': 'success', 'file': csv_path}
        
        return {'status': 'failed', 'error': 'Export failed'}
    
    except Exception as e:
        logger.error(f"Export payroll error: {str(e)}")
        raise


@shared_task(name='technicians.tasks.update_technician_availability')
def update_technician_availability(technician_id: int):
    """
    Update technician availability в Google Calendar.
    Trigger: Schedule.save() signal.
    """
    try:
        from technicians.models import Technician
        
        technician = Technician.objects.get(id=technician_id)
        
        # TODO: Update Google Calendar availability
        logger.info(f"Would update availability for technician {technician_id}")
        
        return {'status': 'success', 'technician_id': technician_id}
    
    except Exception as e:
        logger.error(f"Update availability error: {str(e)}")
        raise

