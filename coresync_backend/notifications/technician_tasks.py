"""
Technician Notification Email Task - Повідомлення для technician про нове бронювання.
"""
from celery import shared_task
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name='notifications.tasks.send_technician_booking_notification')
def send_technician_booking_notification(booking_id: int):
    """
    Send notification до technician про нове бронювання.
    Trigger: після payment succeeded та booking confirmed.
    
    Args:
        booking_id: Booking ID
    """
    try:
        from services.models import Booking
        from .email_sender import EmailSender
        from .models import EmailLog
        
        booking = Booking.objects.get(id=booking_id)
        
        if not booking.technician:
            logger.info(f"Booking {booking_id} has no assigned technician")
            return
        
        # Send email до technician
        sender = EmailSender()
        result = sender.send_technician_booking_notification(booking)
        
        # Log email
        EmailLog.objects.create(
            booking=booking,
            recipient_email=booking.technician.email,
            recipient_name=booking.technician.full_name,
            email_type='technician_notification',
            subject=f'New Booking Assignment - {booking.service.name}',
            status='sent' if result['success'] else 'failed',
            sent_at=timezone.now() if result['success'] else None,
            sendgrid_message_id=result.get('message_id', ''),
            error_message=result.get('error', '')
        )
        
        logger.info(f"Technician notification sent for booking {booking_id}")
        return result
    
    except Exception as e:
        logger.error(f"Error sending technician notification: {str(e)}")
        raise

