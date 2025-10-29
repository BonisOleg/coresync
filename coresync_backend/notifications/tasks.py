"""
Notifications Celery Tasks - Automated email sending.
4 критичні types згідно Full100.md.
"""
from celery import shared_task
import logging
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task(name='notifications.tasks.send_booking_confirmation')
def send_booking_confirmation(booking_id: int):
    """
    Send booking confirmation email.
    Trigger: booking created + payment succeeded.
    """
    try:
        from services.models import Booking
        from .email_sender import EmailSender
        from .models import EmailLog
        
        booking = Booking.objects.get(id=booking_id)
        
        # Check user preferences
        if not _check_email_preference(booking.user, 'email_booking_confirmations'):
            logger.info(f"User {booking.user.email} opted out of confirmations")
            return
        
        # Generate calendar invite
        # from .calendar_invite import generate_ics_file
        # ics_file = generate_ics_file(booking)
        
        # Send email
        sender = EmailSender()
        result = sender.send_booking_confirmation(
            booking=booking,
            # attachment=ics_file
        )
        
        # Log email
        EmailLog.objects.create(
            booking=booking,
            recipient_email=booking.user.email,
            recipient_name=booking.user.get_full_name(),
            email_type='booking_confirmation',
            subject=f'Booking Confirmed - {booking.service.name}',
            status='sent' if result['success'] else 'failed',
            sent_at=timezone.now() if result['success'] else None,
            sendgrid_message_id=result.get('message_id', ''),
            error_message=result.get('error', '')
        )
        
        logger.info(f"Booking confirmation sent for booking {booking_id}")
        return result
    
    except Exception as e:
        logger.error(f"Error sending booking confirmation: {str(e)}")
        raise


@shared_task(name='notifications.tasks.send_24hr_reminder')
def send_24hr_reminder(booking_id: int):
    """
    Send 24-hour reminder email.
    Trigger: Celery beat cron (daily scan).
    """
    try:
        from services.models import Booking
        from .email_sender import EmailSender
        from .models import EmailLog
        
        booking = Booking.objects.get(id=booking_id)
        
        # Check user preferences
        if not _check_email_preference(booking.user, 'email_reminders'):
            return
        
        # Send email
        sender = EmailSender()
        result = sender.send_reminder(booking)
        
        # Log
        EmailLog.objects.create(
            booking=booking,
            recipient_email=booking.user.email,
            recipient_name=booking.user.get_full_name(),
            email_type='booking_reminder',
            subject=f'Reminder: Your appointment tomorrow at {booking.booking_time}',
            status='sent' if result['success'] else 'failed',
            sent_at=timezone.now() if result['success'] else None,
            sendgrid_message_id=result.get('message_id', ''),
            error_message=result.get('error', '')
        )
        
        logger.info(f"Reminder sent for booking {booking_id}")
        return result
    
    except Exception as e:
        logger.error(f"Error sending reminder: {str(e)}")
        raise


@shared_task(name='notifications.tasks.send_review_request')
def send_review_request(booking_id: int):
    """
    Send review request email.
    Trigger: 2 hours after booking end_time.
    """
    try:
        from services.models import Booking
        from .email_sender import EmailSender
        from .models import EmailLog
        
        booking = Booking.objects.get(id=booking_id)
        
        # Check user preferences
        if not _check_email_preference(booking.user, 'email_review_requests'):
            return
        
        # Send email
        sender = EmailSender()
        result = sender.send_review_request(booking)
        
        # Log
        EmailLog.objects.create(
            booking=booking,
            recipient_email=booking.user.email,
            recipient_name=booking.user.get_full_name(),
            email_type='review_request',
            subject='How was your CoreSync experience?',
            status='sent' if result['success'] else 'failed',
            sent_at=timezone.now() if result['success'] else None,
            sendgrid_message_id=result.get('message_id', ''),
            error_message=result.get('error', '')
        )
        
        logger.info(f"Review request sent for booking {booking_id}")
        return result
    
    except Exception as e:
        logger.error(f"Error sending review request: {str(e)}")
        raise


@shared_task(name='notifications.tasks.send_membership_welcome')
def send_membership_welcome(user_id: int):
    """
    Send membership welcome email.
    Trigger: subscription created (Stripe webhook).
    """
    try:
        from users.models import User
        from memberships.models import Membership
        from .email_sender import EmailSender
        from .models import EmailLog
        
        user = User.objects.get(id=user_id)
        membership = Membership.objects.filter(user=user, status='active').first()
        
        if not membership:
            logger.warning(f"No active membership for user {user_id}")
            return
        
        # Generate membership card PDF
        # from .pdf_generator import generate_membership_card
        # pdf_file = generate_membership_card(membership)
        
        # Send email
        sender = EmailSender()
        result = sender.send_membership_welcome(
            user=user,
            membership=membership,
            # attachment=pdf_file
        )
        
        # Log
        EmailLog.objects.create(
            recipient_email=user.email,
            recipient_name=user.get_full_name(),
            email_type='membership_welcome',
            subject=f'Welcome to CoreSync {membership.tier.title()} Membership!',
            status='sent' if result['success'] else 'failed',
            sent_at=timezone.now() if result['success'] else None,
            sendgrid_message_id=result.get('message_id', ''),
            error_message=result.get('error', '')
        )
        
        logger.info(f"Membership welcome sent to user {user_id}")
        return result
    
    except Exception as e:
        logger.error(f"Error sending membership welcome: {str(e)}")
        raise


@shared_task(name='notifications.tasks.send_daily_reminders_batch')
def send_daily_reminders_batch():
    """
    Batch process: Send 24hr reminders для всіх bookings tomorrow.
    Runs daily at 9 AM EST (Celery beat).
    """
    try:
        from services.models import Booking
        
        # Get bookings для tomorrow
        tomorrow = timezone.now().date() + timedelta(days=1)
        
        bookings = Booking.objects.filter(
            booking_date=tomorrow,
            status='confirmed',
            payment_status='paid'
        )
        
        count = 0
        for booking in bookings:
            # Queue individual reminder tasks
            send_24hr_reminder.delay(booking.id)
            count += 1
        
        logger.info(f"Queued {count} reminder emails for {tomorrow}")
        
        return {
            'status': 'success',
            'count': count,
            'date': tomorrow.isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error in daily reminders batch: {str(e)}")
        raise


def _check_email_preference(user, preference_field: str) -> bool:
    """
    Check user email preference.
    
    Args:
        user: User object
        preference_field: Field name (e.g. 'email_reminders')
    
    Returns:
        bool: True if enabled
    """
    try:
        from .models import NotificationPreference
        
        prefs = NotificationPreference.objects.filter(user=user).first()
        
        if not prefs:
            # Default: all enabled
            return True
        
        if not prefs.email_enabled:
            return False
        
        return getattr(prefs, preference_field, True)
    
    except Exception:
        # Default: send email
        return True

