"""
Form submission models for the CoreSync application.
"""
from django.db import models
from core.models import BaseModel


class ContactSubmission(BaseModel):
    """
    Contact form submissions from the website.
    """
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('responded', 'Responded'),
        ('closed', 'Closed'),
        ('spam', 'Spam'),
    ]

    # Form fields
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    
    # Status and processing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    assigned_to = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_contacts'
    )
    
    # Metadata
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    
    # Response tracking
    responded_at = models.DateTimeField(blank=True, null=True)
    response_notes = models.TextField(blank=True)

    class Meta:
        db_table = 'contact_submissions'
        verbose_name = 'Contact Submission'
        verbose_name_plural = 'Contact Submissions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Contact from {self.name} ({self.email})"


class MembershipInquiry(BaseModel):
    """
    Membership inquiry form submissions.
    """
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('scheduled', 'Tour Scheduled'),
        ('converted', 'Converted to Member'),
        ('declined', 'Declined'),
        ('lost', 'Lost Lead'),
    ]

    INTEREST_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('immediate', 'Ready to Join'),
    ]

    # Personal information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    # Membership interest
    interested_plan = models.CharField(
        max_length=100,
        blank=True,
        help_text="Which membership plan they're interested in"
    )
    interest_level = models.CharField(
        max_length=20,
        choices=INTEREST_LEVELS,
        default='medium'
    )
    
    # Preferences
    preferred_services = models.JSONField(
        default=list,
        blank=True,
        help_text="List of services they're interested in"
    )
    preferred_contact_time = models.CharField(max_length=100, blank=True)
    how_heard_about_us = models.CharField(max_length=100, blank=True)
    
    # Additional information
    questions = models.TextField(blank=True)
    special_requests = models.TextField(blank=True)
    
    # Lead management
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    assigned_to = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_leads'
    )
    
    # Follow-up tracking
    last_contact_date = models.DateTimeField(blank=True, null=True)
    next_follow_up_date = models.DateTimeField(blank=True, null=True)
    contact_attempts = models.PositiveIntegerField(default=0)
    
    # Conversion tracking
    converted_user = models.OneToOneField(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='membership_inquiry'
    )
    converted_at = models.DateTimeField(blank=True, null=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    utm_source = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'membership_inquiries'
        verbose_name = 'Membership Inquiry'
        verbose_name_plural = 'Membership Inquiries'
        ordering = ['-created_at']

    def __str__(self):
        return f"Membership inquiry from {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def mark_converted(self, user):
        """Mark this inquiry as converted to a member."""
        self.status = 'converted'
        self.converted_user = user
        self.converted_at = models.timezone.now()
        self.save()


class NewsletterSubscription(BaseModel):
    """
    Newsletter and marketing email subscriptions.
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    
    # Subscription preferences
    marketing_emails = models.BooleanField(default=True)
    service_updates = models.BooleanField(default=True)
    special_offers = models.BooleanField(default=True)
    event_notifications = models.BooleanField(default=False)
    
    # Status
    is_subscribed = models.BooleanField(default=True)
    unsubscribed_at = models.DateTimeField(blank=True, null=True)
    unsubscribe_reason = models.CharField(max_length=255, blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    source = models.CharField(
        max_length=50,
        blank=True,
        help_text="Where the subscription came from"
    )

    class Meta:
        db_table = 'newsletter_subscriptions'
        verbose_name = 'Newsletter Subscription'
        verbose_name_plural = 'Newsletter Subscriptions'
        ordering = ['-created_at']

    def __str__(self):
        status = "Subscribed" if self.is_subscribed else "Unsubscribed"
        return f"{self.email} ({status})"

    def unsubscribe(self, reason=""):
        """Unsubscribe from newsletter."""
        self.is_subscribed = False
        self.unsubscribed_at = models.timezone.now()
        self.unsubscribe_reason = reason
        self.save()
