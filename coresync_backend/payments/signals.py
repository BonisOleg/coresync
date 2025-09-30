"""
Django signals for automatic QuickBooks synchronization.
"""
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from .models import Payment, QuickBooksSync
from .quickbooks_service import quickbooks_service
from services.booking_models import Booking
from memberships.models import Membership

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Payment)
def auto_sync_payment_to_quickbooks(sender, instance, created, **kwargs):
    """
    Automatically schedule QuickBooks sync when payment is successful.
    Ensures ALL payments go to QuickBooks as per client requirements.
    """
    # Only sync successful payments
    if instance.status != 'succeeded':
        return
    
    # Check if already scheduled or completed
    existing_sync = QuickBooksSync.objects.filter(
        sync_type='payment',
        object_id=str(instance.id)
    ).first()
    
    if existing_sync and existing_sync.status == 'completed':
        return  # Already synced successfully
    
    try:
        # Schedule sync
        sync_record, created = QuickBooksSync.objects.get_or_create(
            sync_type='payment',
            object_id=str(instance.id),
            defaults={
                'status': 'pending',
                'sync_data': {
                    'payment_type': instance.payment_type,
                    'payment_method': instance.payment_method,
                    'amount': str(instance.amount),
                    'customer_name': instance.user.full_name,
                    'scheduled_at': timezone.now().isoformat(),
                }
            }
        )
        
        if created:
            logger.info(f"Scheduled QuickBooks sync for payment {instance.payment_id}")
            
            # Trigger immediate sync via Celery task
            if quickbooks_service.is_configured():
                from .tasks import sync_specific_payment
                sync_specific_payment.delay(instance.id)
                logger.info(f"Scheduled immediate QuickBooks sync for payment {instance.payment_id}")
            else:
                logger.warning(f"QuickBooks not configured - payment {instance.payment_id} sync delayed")
    
    except Exception as e:
        logger.error(f"Failed to schedule QuickBooks sync for payment {instance.payment_id}: {e}")


@receiver(post_save, sender=Booking)
def auto_sync_booking_to_quickbooks(sender, instance, created, **kwargs):
    """
    Automatically schedule QuickBooks invoice sync when booking is confirmed.
    """
    # Only sync confirmed or completed bookings
    if instance.status not in ['confirmed', 'completed']:
        return
    
    # Check if already scheduled or completed
    existing_sync = QuickBooksSync.objects.filter(
        sync_type='invoice',
        object_id=str(instance.id)
    ).first()
    
    if existing_sync and existing_sync.status == 'completed':
        return  # Already synced successfully
    
    try:
        # Schedule invoice sync
        sync_record, created = QuickBooksSync.objects.get_or_create(
            sync_type='invoice',
            object_id=str(instance.id),
            defaults={
                'status': 'pending',
                'sync_data': {
                    'booking_reference': instance.booking_reference,
                    'customer_name': instance.user.full_name,
                    'service_name': instance.service.name,
                    'total_amount': str(instance.final_total),
                    'booking_date': instance.booking_date.isoformat(),
                    'scheduled_at': timezone.now().isoformat(),
                }
            }
        )
        
        if created:
            logger.info(f"Scheduled QuickBooks invoice sync for booking {instance.booking_reference}")
            
            # Trigger immediate sync via Celery task
            if quickbooks_service.is_configured():
                from .tasks import sync_specific_booking
                sync_specific_booking.delay(instance.id)
                logger.info(f"Scheduled immediate QuickBooks sync for booking {instance.booking_reference}")
            else:
                logger.warning(f"QuickBooks not configured - booking {instance.booking_reference} sync delayed")
    
    except Exception as e:
        logger.error(f"Failed to schedule QuickBooks sync for booking {instance.booking_reference}: {e}")


@receiver(post_save, sender=Membership)
def auto_sync_membership_payment_to_quickbooks(sender, instance, created, **kwargs):
    """
    Automatically sync membership payments to QuickBooks.
    """
    # Only sync active memberships with payment history
    if instance.status != 'active':
        return
    
    try:
        # Get membership payments
        membership_payments = Payment.objects.filter(
            membership=instance,
            status='succeeded',
            payment_type='membership'
        )
        
        for payment in membership_payments:
            # Check if already synced
            existing_sync = QuickBooksSync.objects.filter(
                sync_type='payment',
                object_id=str(payment.id),
                status='completed'
            ).first()
            
            if not existing_sync:
                # Schedule membership payment sync
                QuickBooksSync.objects.get_or_create(
                    sync_type='payment',
                    object_id=str(payment.id),
                    defaults={
                        'status': 'pending',
                        'sync_data': {
                            'payment_type': 'membership',
                            'membership_plan': instance.plan.name,
                            'customer_name': instance.user.full_name,
                            'amount': str(payment.amount),
                            'scheduled_at': timezone.now().isoformat(),
                        }
                    }
                )
                logger.info(f"Scheduled QuickBooks sync for membership payment {payment.payment_id}")
    
    except Exception as e:
        logger.error(f"Failed to schedule QuickBooks sync for membership {instance.id}: {e}")


@receiver(post_save, sender='users.User')
def auto_sync_customer_to_quickbooks(sender, instance, created, **kwargs):
    """
    Automatically sync new users to QuickBooks as customers.
    """
    # Skip if user is not complete or is staff
    if not instance.email or instance.is_staff:
        return
    
    # Check if already synced
    existing_sync = QuickBooksSync.objects.filter(
        sync_type='customer',
        object_id=str(instance.id),
        status='completed'
    ).first()
    
    if existing_sync:
        return  # Already synced
    
    try:
        # Schedule customer sync
        sync_record, created_sync = QuickBooksSync.objects.get_or_create(
            sync_type='customer',
            object_id=str(instance.id),
            defaults={
                'status': 'pending',
                'sync_data': {
                    'customer_name': instance.full_name,
                    'email': instance.email,
                    'is_member': hasattr(instance, 'membership') and instance.membership.is_active,
                    'scheduled_at': timezone.now().isoformat(),
                }
            }
        )
        
        if created_sync:
            logger.info(f"Scheduled QuickBooks customer sync for user {instance.email}")
            
            # Try immediate sync if QuickBooks is configured
            if quickbooks_service.is_configured():
                success, qb_id, message = quickbooks_service.sync_customer(instance)
                if success:
                    logger.info(f"Immediately synced customer {instance.email} to QuickBooks")
                else:
                    logger.warning(f"Immediate sync failed for customer {instance.email}: {message}")
    
    except Exception as e:
        logger.error(f"Failed to schedule QuickBooks sync for user {instance.email}: {e}")


# Auto-run sync queue processor
def process_quickbooks_queue_periodically():
    """
    Function to be called by scheduler (Celery, cron, etc.)
    Processes pending QuickBooks sync items.
    """
    if not quickbooks_service.is_configured():
        logger.warning("QuickBooks not configured - skipping sync queue processing")
        return
    
    try:
        results = quickbooks_service.process_sync_queue(max_items=20)
        
        if 'error' not in results:
            logger.info(
                f"Processed QuickBooks sync queue: "
                f"{results['successful']} successful, {results['failed']} failed"
            )
            
            if results['errors']:
                for error in results['errors']:
                    logger.error(f"QuickBooks sync error: {error}")
        else:
            logger.error(f"QuickBooks queue processing failed: {results['error']}")
    
    except Exception as e:
        logger.error(f"QuickBooks queue processing exception: {e}")
