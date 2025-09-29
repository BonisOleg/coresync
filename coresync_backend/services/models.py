"""
Service models for the CoreSync application.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseModel


class ServiceCategory(BaseModel):
    """
    Categories for spa services (Mensuite, Coresync Private, etc.)
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    
    # Display order
    order = models.PositiveIntegerField(default=0)
    
    # Features and technology
    featured_technologies = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'service_categories'
        verbose_name = 'Service Category'
        verbose_name_plural = 'Service Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Service(BaseModel):
    """
    Individual spa services offered at CoreSync.
    """
    DURATION_CHOICES = [
        (30, '30 minutes'),
        (45, '45 minutes'),
        (60, '1 hour'),
        (75, '1 hour 15 minutes'),
        (90, '1 hour 30 minutes'),
        (120, '2 hours'),
        (150, '2 hours 30 minutes'),
        (180, '3 hours'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.CASCADE,
        related_name='services'
    )
    
    # Pricing
    member_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    non_member_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Duration and logistics
    duration = models.PositiveIntegerField(
        choices=DURATION_CHOICES,
        help_text="Duration in minutes"
    )
    max_capacity = models.PositiveIntegerField(
        default=1,
        help_text="Maximum number of people for this service"
    )
    
    # Features
    requires_appointment = models.BooleanField(default=True)
    member_only = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    
    # Media
    main_image = models.ImageField(upload_to='services/', blank=True, null=True)
    gallery_images = models.JSONField(default=list, blank=True)
    video_url = models.URLField(blank=True)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    
    # Display order
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'services'
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ['category', 'order', 'name']

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    @property
    def savings_for_members(self):
        """Calculate savings for members."""
        return self.non_member_price - self.member_price

    @property
    def member_discount_percentage(self):
        """Calculate member discount percentage."""
        if self.non_member_price > 0:
            return round((self.savings_for_members / self.non_member_price) * 100, 1)
        return 0

    def get_price_for_user(self, user):
        """Get price based on user membership status."""
        if user and user.is_authenticated and user.is_member:
            return self.member_price
        return self.non_member_price


class ServiceAddon(BaseModel):
    """
    Add-ons that can be purchased with services.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Applicable services
    services = models.ManyToManyField(
        Service,
        related_name='addons',
        blank=True
    )
    
    # Availability
    available_for_all_services = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'service_addons'
        verbose_name = 'Service Add-on'
        verbose_name_plural = 'Service Add-ons'
        ordering = ['name']

    def __str__(self):
        return self.name


class ServiceHistory(BaseModel):
    """
    History of services used by customers.
    """
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='service_history'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='history'
    )
    
    # Service details
    service_date = models.DateTimeField()
    completion_date = models.DateTimeField(blank=True, null=True)
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Add-ons purchased
    addons = models.ManyToManyField(ServiceAddon, blank=True)
    addons_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    # Feedback and rating
    rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    feedback = models.TextField(blank=True)
    
    # Internal notes
    staff_notes = models.TextField(blank=True)
    
    # Payment information
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('refunded', 'Refunded'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )

    class Meta:
        db_table = 'service_history'
        verbose_name = 'Service History'
        verbose_name_plural = 'Service Histories'
        ordering = ['-service_date']

    def __str__(self):
        return f"{self.user.full_name} - {self.service.name} on {self.service_date.date()}"

    @property
    def total_amount(self):
        """Calculate total amount including add-ons."""
        return self.price_paid + self.addons_total
