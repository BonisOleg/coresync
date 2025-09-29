"""
Membership models for the CoreSync application.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseModel
from datetime import datetime, timedelta


class MembershipPlan(BaseModel):
    """
    Membership plans available for customers.
    """
    DURATION_CHOICES = [
        (1, '1 Month'),
        (3, '3 Months'),
        (6, '6 Months'),
        (12, '12 Months'),
        (24, '24 Months'),
    ]

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    
    # Pricing
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    duration_months = models.PositiveIntegerField(choices=DURATION_CHOICES)
    
    # Benefits and features
    benefits = models.JSONField(
        default=list,
        help_text="List of membership benefits"
    )
    discount_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(100)],
        help_text="Discount percentage on services"
    )
    
    # Access levels
    mensuite_access = models.BooleanField(default=True)
    coresync_private_access = models.BooleanField(default=True)
    iot_control_access = models.BooleanField(default=True)
    priority_booking = models.BooleanField(default=False)
    
    # Limits and quotas
    monthly_service_credits = models.PositiveIntegerField(
        default=0,
        help_text="Number of free services per month (0 = unlimited)"
    )
    guest_passes = models.PositiveIntegerField(
        default=0,
        help_text="Number of guest passes included"
    )
    
    # Display
    featured = models.BooleanField(default=False)
    color_scheme = models.CharField(max_length=7, default='#000000')  # Hex color
    icon = models.CharField(max_length=50, blank=True)  # FontAwesome icon class
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'membership_plans'
        verbose_name = 'Membership Plan'
        verbose_name_plural = 'Membership Plans'
        ordering = ['order', 'price']

    def __str__(self):
        return f"{self.name} (${self.price}/{self.get_duration_months_display()})"

    @property
    def monthly_price(self):
        """Calculate monthly price."""
        return round(self.price / self.duration_months, 2)

    def calculate_savings_example(self, services_per_month=2):
        """Calculate example savings for marketing."""
        # This would need to be calculated based on average service prices
        # For now, return a placeholder
        average_service_price = 100  # This should be dynamic
        monthly_savings = (average_service_price * services_per_month) * (self.discount_percentage / 100)
        return round(monthly_savings, 2)


class Membership(BaseModel):
    """
    Active membership for a user.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('suspended', 'Suspended'),
    ]

    user = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        related_name='membership'
    )
    plan = models.ForeignKey(
        MembershipPlan,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    
    # Usage tracking
    services_used_this_month = models.PositiveIntegerField(default=0)
    guest_passes_used = models.PositiveIntegerField(default=0)
    
    # Payment information
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    auto_renew = models.BooleanField(default=True)
    
    # Notes
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'memberships'
        verbose_name = 'Membership'
        verbose_name_plural = 'Memberships'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.user.full_name} - {self.plan.name}"

    @property
    def is_active(self):
        """Check if membership is currently active."""
        return (
            self.status == 'active' and
            self.start_date <= datetime.now().date() <= self.end_date
        )

    @property
    def days_remaining(self):
        """Calculate days remaining in membership."""
        if self.end_date > datetime.now().date():
            return (self.end_date - datetime.now().date()).days
        return 0

    def can_use_service_credit(self):
        """Check if user can use monthly service credit."""
        if self.plan.monthly_service_credits == 0:  # Unlimited
            return True
        return self.services_used_this_month < self.plan.monthly_service_credits

    def use_service_credit(self):
        """Use one service credit."""
        if self.can_use_service_credit():
            self.services_used_this_month += 1
            self.save()
            return True
        return False

    def reset_monthly_usage(self):
        """Reset monthly usage counters."""
        self.services_used_this_month = 0
        self.save()


class MembershipBenefit(models.Model):
    """
    Individual benefits that can be assigned to membership plans.
    """
    BENEFIT_TYPES = [
        ('discount', 'Discount'),
        ('access', 'Special Access'),
        ('service', 'Free Service'),
        ('amenity', 'Amenity'),
        ('priority', 'Priority'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    benefit_type = models.CharField(max_length=20, choices=BENEFIT_TYPES)
    icon = models.CharField(max_length=50, blank=True)  # FontAwesome icon
    
    # Value (for discounts, quantities, etc.)
    value = models.CharField(max_length=50, blank=True)
    
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'membership_benefits'
        verbose_name = 'Membership Benefit'
        verbose_name_plural = 'Membership Benefits'
        ordering = ['name']

    def __str__(self):
        return self.name
