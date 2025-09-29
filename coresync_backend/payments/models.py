"""
Payment models for the CoreSync application.
"""
from django.db import models
from django.core.validators import MinValueValidator
from core.models import BaseModel
import uuid


class Payment(BaseModel):
    """
    Payment records for services and memberships.
    """
    PAYMENT_TYPES = [
        ('service', 'Service Payment'),
        ('membership', 'Membership Payment'),
        ('addon', 'Add-on Payment'),
        ('product', 'Product Purchase'),
        ('refund', 'Refund'),
    ]

    PAYMENT_METHODS = [
        ('stripe_card', 'Credit/Debit Card'),
        ('stripe_apple_pay', 'Apple Pay'),
        ('stripe_google_pay', 'Google Pay'),
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    ]

    # Unique identifier
    payment_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # Customer information
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    
    # Payment details
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    currency = models.CharField(max_length=3, default='USD')
    
    # Status and processing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processed_at = models.DateTimeField(blank=True, null=True)
    
    # External payment processor references
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    stripe_charge_id = models.CharField(max_length=255, blank=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    
    # QuickBooks integration
    quickbooks_payment_id = models.CharField(max_length=255, blank=True)
    quickbooks_synced = models.BooleanField(default=False)
    quickbooks_sync_error = models.TextField(blank=True)
    
    # Related objects
    service_history = models.ForeignKey(
        'services.ServiceHistory',
        on_delete=models.CASCADE,
        related_name='payments',
        null=True,
        blank=True
    )
    membership = models.ForeignKey(
        'memberships.Membership',
        on_delete=models.CASCADE,
        related_name='payments',
        null=True,
        blank=True
    )
    
    # Additional details
    description = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Refund information
    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    refund_reason = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.payment_id} - {self.user.full_name} - ${self.amount}"

    @property
    def is_successful(self):
        return self.status == 'succeeded'

    @property
    def net_amount(self):
        """Amount after refunds."""
        return self.amount - self.refund_amount

    def can_be_refunded(self):
        """Check if payment can be refunded."""
        return (
            self.status == 'succeeded' and
            self.refund_amount < self.amount
        )


class StripeWebhookEvent(models.Model):
    """
    Log of Stripe webhook events for debugging and reconciliation.
    """
    stripe_event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=100)
    event_data = models.JSONField()
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'stripe_webhook_events'
        verbose_name = 'Stripe Webhook Event'
        verbose_name_plural = 'Stripe Webhook Events'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event_type} - {self.stripe_event_id}"


class QuickBooksSync(BaseModel):
    """
    QuickBooks synchronization tracking.
    """
    SYNC_TYPES = [
        ('payment', 'Payment Sync'),
        ('customer', 'Customer Sync'),
        ('service', 'Service Sync'),
        ('invoice', 'Invoice Sync'),
    ]

    SYNC_STATUS = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ]

    sync_type = models.CharField(max_length=20, choices=SYNC_TYPES)
    object_id = models.CharField(max_length=255)  # Local object ID
    quickbooks_id = models.CharField(max_length=255, blank=True)  # QB object ID
    
    status = models.CharField(max_length=20, choices=SYNC_STATUS, default='pending')
    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=3)
    
    last_attempt_at = models.DateTimeField(blank=True, null=True)
    next_attempt_at = models.DateTimeField(blank=True, null=True)
    
    error_message = models.TextField(blank=True)
    sync_data = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'quickbooks_sync'
        verbose_name = 'QuickBooks Sync'
        verbose_name_plural = 'QuickBooks Syncs'
        ordering = ['-created_at']
        unique_together = ['sync_type', 'object_id']

    def __str__(self):
        return f"{self.get_sync_type_display()} - {self.object_id} ({self.status})"

    def can_retry(self):
        """Check if sync can be retried."""
        return self.attempts < self.max_attempts and self.status == 'failed'
