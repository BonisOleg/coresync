"""
Shop models for CoreSync retail functionality.
All products are pickup-only (no shipping).
"""
from django.db import models
from django.db import transaction
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from core.models import BaseModel


class Product(BaseModel):
    """Retail products available for member pickup."""
    
    CATEGORIES = (
        ('skincare', 'Skincare'),
        ('wellness', 'Wellness Tech'),
        ('accessories', 'Accessories'),
        ('supplements', 'Supplements'),
    )
    
    # Basic Information
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    
    # Pricing (with validation - FIXED)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Regular price for non-members"
    )
    member_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Discounted price for members"
    )
    member_discount_percent = models.PositiveIntegerField(
        default=10,
        help_text="Discount percentage (for display)"
    )
    
    # Inventory (with validation - FIXED)
    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Current stock quantity"
    )
    low_stock_threshold = models.IntegerField(
        default=5,
        validators=[MinValueValidator(0)],
        help_text="Alert when stock falls below this"
    )
    
    # Media
    main_image = models.ImageField(
        upload_to='products/',
        blank=True,
        help_text="Primary product image"
    )
    gallery_images = models.JSONField(
        default=list,
        blank=True,
        help_text="Additional product images (list of URLs)"
    )
    
    # Availability
    # NOTE: is_active inherited from BaseModel - NO DUPLICATE!
    is_featured = models.BooleanField(
        default=False,
        help_text="Show on featured products section"
    )
    
    # QuickBooks Integration
    quickbooks_item_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="QuickBooks item ID for sync"
    )
    quickbooks_synced = models.BooleanField(default=False)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    
    class Meta:
        db_table = 'shop_products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['is_featured', 'is_active']),
            models.Index(fields=['slug']),
        ]
    
    def clean(self):
        """Validate model data - ADDED FOR SAFETY"""
        super().clean()
        
        # Member price must be less than regular price
        if self.member_price >= self.price:
            raise ValidationError({
                'member_price': 'Member price must be less than regular price'
            })
    
    def save(self, *args, **kwargs):
        """Override save to always validate"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    @property
    def savings_amount(self):
        """Calculate savings for members"""
        return self.price - self.member_price
    
    @property
    def discount_percentage(self):
        """Calculate actual discount percentage"""
        if self.price > 0:
            return round(((self.price - self.member_price) / self.price) * 100, 1)
        return 0
    
    @property
    def in_stock(self):
        """Check if product is in stock"""
        return self.stock > 0
    
    @property
    def is_low_stock(self):
        """Check if stock is low"""
        return 0 < self.stock <= self.low_stock_threshold


class PickupOrder(BaseModel):
    """Orders for pickup at spa (no shipping)."""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('ready', 'Ready for Pickup'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    # Unique order identifier
    order_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text="Format: PO-YYYY-NNNNNN"
    )
    
    # Customer
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='pickup_orders'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Pickup Details
    pickup_date = models.DateField(
        blank=True,
        null=True,
        help_text="Scheduled pickup date"
    )
    pickup_booking = models.ForeignKey(
        'services.Booking',  # String reference - NO circular import
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pickup_orders',
        help_text="Link to spa booking for pickup"
    )
    
    # Pricing (with validation - FIXED)
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Payment
    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pickup_orders'
    )
    paid_at = models.DateTimeField(blank=True, null=True)
    
    # Notes
    customer_notes = models.TextField(
        blank=True,
        help_text="Customer instructions or requests"
    )
    staff_notes = models.TextField(
        blank=True,
        help_text="Internal staff notes"
    )
    
    # QuickBooks Integration
    quickbooks_synced = models.BooleanField(default=False)
    quickbooks_invoice_id = models.CharField(max_length=100, blank=True)
    quickbooks_sync_error = models.TextField(blank=True)
    
    class Meta:
        db_table = 'pickup_orders'
        verbose_name = 'Pickup Order'
        verbose_name_plural = 'Pickup Orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'pickup_date']),
            models.Index(fields=['order_number']),
        ]
    
    def save(self, *args, **kwargs):
        """Generate unique order number - RACE CONDITION FIXED"""
        if not self.order_number:
            from django.utils import timezone
            
            year = timezone.now().year
            
            # Use atomic transaction with row-level lock
            with transaction.atomic():
                # Lock the last order to prevent race condition
                last_order = PickupOrder.objects.select_for_update().filter(
                    order_number__startswith=f'PO-{year}-'
                ).order_by('-order_number').first()
                
                if last_order:
                    # Extract number and increment
                    last_num = int(last_order.order_number.split('-')[-1])
                    next_num = last_num + 1
                else:
                    # First order of the year
                    next_num = 1
                
                self.order_number = f'PO-{year}-{next_num:06d}'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.order_number} - {self.user.full_name}"
    
    @property
    def items_count(self):
        """Total number of items in order"""
        return self.items.count()
    
    @property
    def can_be_cancelled(self):
        """Check if order can be cancelled"""
        return self.status in ['pending', 'processing']


class OrderItem(BaseModel):
    """Individual items in a pickup order."""
    
    order = models.ForeignKey(
        PickupOrder,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    
    # Quantity and Pricing (with validation - FIXED)
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Price per unit at time of order"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="unit_price * quantity"
    )
    
    # Additional Info
    notes = models.CharField(
        max_length=255,
        blank=True,
        help_text="Special requests for this item"
    )
    
    class Meta:
        db_table = 'order_items'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
    
    def save(self, *args, **kwargs):
        """Auto-calculate total price"""
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
