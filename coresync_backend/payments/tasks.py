"""
Celery tasks for QuickBooks synchronization.
"""
import logging
from celery import shared_task
from django.utils import timezone
from django.db import models
from datetime import timedelta

from .quickbooks_service import quickbooks_service
from .models import QuickBooksSync

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def sync_quickbooks_queue(self, max_items=50):
    """
    Process QuickBooks sync queue automatically.
    This task should be run periodically (every 5-10 minutes).
    """
    try:
        if not quickbooks_service.is_configured():
            logger.warning("QuickBooks not configured - skipping sync")
            return {'status': 'skipped', 'reason': 'not_configured'}
        
        results = quickbooks_service.process_sync_queue(max_items)
        
        if 'error' in results:
            logger.error(f"QuickBooks sync queue failed: {results['error']}")
            raise Exception(results['error'])
        
        logger.info(
            f"QuickBooks sync completed: {results['successful']} successful, "
            f"{results['failed']} failed, {results['processed']} total"
        )
        
        return {
            'status': 'completed',
            'results': results
        }
        
    except Exception as e:
        logger.error(f"QuickBooks sync task failed: {e}")
        # Retry with exponential backoff
        countdown = 2 ** self.request.retries * 60  # 1min, 2min, 4min
        raise self.retry(exc=e, countdown=countdown)


@shared_task
def sync_specific_payment(payment_id):
    """
    Sync a specific payment to QuickBooks immediately.
    """
    try:
        from .models import Payment
        
        payment = Payment.objects.get(id=payment_id)
        
        if not quickbooks_service.is_configured():
            logger.warning(f"QuickBooks not configured - cannot sync payment {payment.payment_id}")
            return {'status': 'skipped', 'reason': 'not_configured'}
        
        success, qb_id, message = quickbooks_service.sync_payment(payment)
        
        if success:
            logger.info(f"Successfully synced payment {payment.payment_id} to QuickBooks: {qb_id}")
            return {'status': 'success', 'quickbooks_id': qb_id}
        else:
            logger.error(f"Failed to sync payment {payment.payment_id}: {message}")
            return {'status': 'failed', 'error': message}
            
    except Payment.DoesNotExist:
        logger.error(f"Payment {payment_id} not found")
        return {'status': 'failed', 'error': 'Payment not found'}
    except Exception as e:
        logger.error(f"Unexpected error syncing payment {payment_id}: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def sync_specific_booking(booking_id):
    """
    Sync a specific booking invoice to QuickBooks immediately.
    """
    try:
        from services.booking_models import Booking
        
        booking = Booking.objects.get(id=booking_id)
        
        if not quickbooks_service.is_configured():
            logger.warning(f"QuickBooks not configured - cannot sync booking {booking.booking_reference}")
            return {'status': 'skipped', 'reason': 'not_configured'}
        
        success, qb_id, message = quickbooks_service.sync_booking_invoice(booking)
        
        if success:
            logger.info(f"Successfully synced booking {booking.booking_reference} to QuickBooks: {qb_id}")
            return {'status': 'success', 'quickbooks_id': qb_id}
        else:
            logger.error(f"Failed to sync booking {booking.booking_reference}: {message}")
            return {'status': 'failed', 'error': message}
            
    except Booking.DoesNotExist:
        logger.error(f"Booking {booking_id} not found")
        return {'status': 'failed', 'error': 'Booking not found'}
    except Exception as e:
        logger.error(f"Unexpected error syncing booking {booking_id}: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def cleanup_old_sync_records():
    """
    Cleanup old completed QuickBooks sync records.
    Keeps records for 90 days for auditing.
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=90)
        
        # Delete old completed sync records
        deleted_count = QuickBooksSync.objects.filter(
            status='completed',
            updated_at__lt=cutoff_date
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} old QuickBooks sync records")
        
        return {
            'status': 'completed',
            'deleted_count': deleted_count
        }
        
    except Exception as e:
        logger.error(f"Failed to cleanup old sync records: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def retry_failed_quickbooks_syncs():
    """
    Retry failed QuickBooks sync attempts.
    """
    try:
        if not quickbooks_service.is_configured():
            logger.warning("QuickBooks not configured - skipping retry")
            return {'status': 'skipped', 'reason': 'not_configured'}
        
        # Get failed syncs that can be retried
        failed_syncs = QuickBooksSync.objects.filter(
            status='failed'
        ).filter(
            attempts__lt=models.F('max_attempts')
        )[:20]  # Limit to 20 at a time
        
        if not failed_syncs.exists():
            return {'status': 'completed', 'message': 'No failed syncs to retry'}
        
        retry_count = 0
        success_count = 0
        
        for sync_item in failed_syncs:
            # Reset for retry
            sync_item.status = 'pending'
            sync_item.error_message = ''
            sync_item.save()
            retry_count += 1
        
        # Process the retries
        results = quickbooks_service.process_sync_queue(max_items=retry_count)
        
        logger.info(f"Retried {retry_count} failed QuickBooks syncs")
        
        return {
            'status': 'completed',
            'retried_count': retry_count,
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Failed to retry QuickBooks syncs: {e}")
        return {'status': 'failed', 'error': str(e)}
