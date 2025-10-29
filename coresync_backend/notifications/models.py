"""
Notifications Models - Email logging and preferences.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class EmailLog(models.Model):
    """
    Email sending log - tracking all automated emails.
    """
    EMAIL_TYPES = [
        ('booking_confirmation', 'Booking Confirmation'),
        ('booking_reminder', '24hr Reminder'),
        ('review_request', 'Review Request'),
        ('membership_welcome', 'Membership Welcome'),
        ('technician_notification', 'Technician Notification'),
        ('password_reset', 'Password Reset'),
        ('payment_receipt', 'Payment Receipt'),
        ('cancellation', 'Booking Cancellation'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
    ]
    
    # Link to booking (якщо applicable)
    booking = models.ForeignKey(
        'services.Booking',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_logs'
    )
    
    # Recipient
    recipient_email = models.EmailField()
    recipient_name = models.CharField(max_length=255, blank=True)
    
    # Email details
    email_type = models.CharField(max_length=30, choices=EMAIL_TYPES)
    subject = models.CharField(max_length=255)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    
    # SendGrid tracking
    sendgrid_message_id = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['email_type', '-created_at']),
            models.Index(fields=['booking', '-created_at']),
        ]
        verbose_name = "Email Log"
        verbose_name_plural = "Email Logs"
    
    def __str__(self):
        return f"{self.get_email_type_display()} → {self.recipient_email} ({self.status})"
    
    def mark_sent(self, message_id=None):
        """Mark email as successfully sent."""
        self.status = 'sent'
        self.sent_at = timezone.now()
        if message_id:
            self.sendgrid_message_id = message_id
        self.save(update_fields=['status', 'sent_at', 'sendgrid_message_id'])
    
    def mark_failed(self, error_msg):
        """Mark email as failed."""
        self.status = 'failed'
        self.error_message = error_msg
        self.retry_count += 1
        self.save(update_fields=['status', 'error_message', 'retry_count'])


class NotificationPreference(models.Model):
    """
    User notification preferences.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Email preferences
    email_enabled = models.BooleanField(
        default=True,
        help_text="Receive email notifications"
    )
    email_booking_confirmations = models.BooleanField(default=True)
    email_reminders = models.BooleanField(default=True)
    email_review_requests = models.BooleanField(default=True)
    email_marketing = models.BooleanField(default=False)
    
    # SMS preferences (Phase 2)
    sms_enabled = models.BooleanField(default=False)
    sms_phone = models.CharField(max_length=20, blank=True)
    
    # Push notifications (Phase 2)
    push_enabled = models.BooleanField(default=False)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Notification Preference"
        verbose_name_plural = "Notification Preferences"
    
    def __str__(self):
        return f"{self.user.email} - Preferences"
