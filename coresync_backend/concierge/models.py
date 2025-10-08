"""
Concierge request models with all fixes applied.
"""
from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from core.models import BaseModel


class ConciergeRequest(BaseModel):
    """Personal concierge requests for premium members."""
    
    REQUEST_TYPES = (
        ('alcohol', 'Premium Alcohol 🥃'),
        ('flowers', 'Fresh Flowers 🌹'),
        ('food', 'Gourmet Food 🍽️'),
        ('jewelry', 'Jewelry & Accessories 💎'),
        ('luxury', 'Luxury Items ✨'),
        ('gift', 'Gift Items 🎁'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('ready', 'Ready for Pickup'),
        ('completed', 'Completed'),
        ('declined', 'Declined'),
        ('cancelled', 'Cancelled'),
    )
    
    # Unique identifier
    request_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text="Format: CR-YYYY-NNNNNN"
    )
    
    # Customer
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='concierge_requests'
    )
    
    # Request Details
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    title = models.CharField(
        max_length=200,
        help_text="Brief title of request"
    )
    description = models.TextField(help_text="Detailed description")
    product_link = models.URLField(
        blank=True,
        help_text="Optional product link"
    )
    
    # Budget (with validation - FIXED)
    budget_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    budget_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    actual_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    # Scheduling
    preferred_pickup_date = models.DateField()
    pickup_booking = models.ForeignKey(
        'services.Booking',  # String reference
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='concierge_requests',
        help_text="Link to booking for pickup"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    # Staff Notes
    admin_notes = models.TextField(
        blank=True,
        help_text="Internal staff notes"
    )
    decline_reason = models.TextField(blank=True)
    
    # Verification
    requires_age_verification = models.BooleanField(
        default=False,
        help_text="For alcohol purchases"
    )
    age_verified = models.BooleanField(default=False)
    
    # Payment
    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='concierge_requests'
    )
    paid_at = models.DateTimeField(blank=True, null=True)
    
    # QuickBooks
    quickbooks_synced = models.BooleanField(default=False)
    quickbooks_invoice_id = models.CharField(max_length=100, blank=True)
    quickbooks_sync_error = models.TextField(blank=True)
    
    # Attachments
    attachments = models.JSONField(
        default=list,
        blank=True,
        help_text="Reference images or links"
    )
    
    class Meta:
        db_table = 'concierge_requests'
        verbose_name = 'Concierge Request'
        verbose_name_plural = 'Concierge Requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'preferred_pickup_date']),
        ]
    
    def clean(self):
        """Validate budget range"""
        super().clean()
        
        if self.budget_min > self.budget_max:
            raise ValidationError({
                'budget_max': 'Maximum budget must be greater than minimum'
            })
    
    def save(self, *args, **kwargs):
        """Generate unique request number - RACE CONDITION FIXED"""
        if not self.request_number:
            from django.utils import timezone
            
            year = timezone.now().year
            
            with transaction.atomic():
                last_request = ConciergeRequest.objects.select_for_update().filter(
                    request_number__startswith=f'CR-{year}-'
                ).order_by('-request_number').first()
                
                if last_request:
                    last_num = int(last_request.request_number.split('-')[-1])
                    next_num = last_num + 1
                else:
                    next_num = 1
                
                self.request_number = f'CR-{year}-{next_num:06d}'
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.request_number} - {self.user.full_name} - {self.title}"
    
    @property
    def is_within_budget(self):
        """Check if actual cost is within budget"""
        if self.actual_cost > 0:
            return self.budget_min <= self.actual_cost <= self.budget_max
        return True
    
    @property
    def can_be_approved(self):
        return self.status == 'pending'
    
    @property
    def can_be_cancelled(self):
        return self.status in ['pending', 'approved', 'processing']
