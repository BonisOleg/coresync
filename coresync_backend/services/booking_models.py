"""
Booking models for the CoreSync application.
Separate file to avoid conflicts with existing models.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import datetime, timedelta, time as dt_time
from core.models import BaseModel
import uuid


class Room(BaseModel):
    """
    Physical rooms where services are provided.
    """
    ROOM_TYPES = [
        ('mensuite', 'Mensuite Room'),
        ('private', 'Coresync Private Room'),
        ('shared', 'Shared Space'),
        ('vip', 'VIP Suite'),
    ]

    name = models.CharField(max_length=100)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    capacity = models.PositiveIntegerField(default=1)
    
    # Features and amenities
    features = models.JSONField(
        default=list,
        help_text="List of room features (e.g., ['AI_massage_bed', 'smart_mirror', 'aromatherapy'])"
    )
    
    # IoT equipment
    has_iot_control = models.BooleanField(default=True)
    iot_device_ids = models.JSONField(
        default=list,
        help_text="List of connected IoT device IDs"
    )
    
    # Availability
    is_active = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    
    # Operating hours
    opening_time = models.TimeField(default=dt_time(9, 0))
    closing_time = models.TimeField(default=dt_time(21, 0))
    
    # Pricing modifiers
    premium_modifier = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        help_text="Multiplier for room pricing (1.0 = standard, 1.2 = 20% premium)"
    )

    class Meta:
        db_table = 'booking_rooms'
        verbose_name = 'Booking Room'
        verbose_name_plural = 'Booking Rooms'
        ordering = ['room_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"

    def is_available_at(self, date_time):
        """Check if room is available at specific datetime."""
        # Check maintenance mode
        if self.maintenance_mode:
            return False
            
        # Check operating hours
        time_only = date_time.time()
        if not (self.opening_time <= time_only <= self.closing_time):
            return False
            
        # Check for existing bookings
        return not self.bookings.filter(
            booking_date=date_time.date(),
            start_time__lte=time_only,
            end_time__gt=time_only,
            status__in=['confirmed', 'in_progress']
        ).exists()


class Booking(BaseModel):
    """
    Main booking model with priority access logic for members.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
        ('rescheduled', 'Rescheduled'),
    ]

    # Unique booking reference
    booking_reference = models.CharField(
        max_length=20, 
        unique=True, 
        editable=False,
        help_text="Format: CS-YYYY-NNNNNN"
    )
    
    # Customer information
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    guest_name = models.CharField(
        max_length=100, 
        blank=True,
        help_text="For bookings made by members for guests"
    )
    guest_phone = models.CharField(max_length=20, blank=True)
    guest_email = models.EmailField(blank=True)
    
    # Service details
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    
    # Scheduling
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    
    # Status and priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_priority_booking = models.BooleanField(
        default=False,
        help_text="Priority bookings for members (2-3 months advance)"
    )
    booking_tier = models.CharField(
        max_length=20,
        choices=[
            ('member_priority', 'Member Priority (2-3 months)'),
            ('member_standard', 'Member Standard'),
            ('non_member', 'Non-Member (3 days only)'),
            ('vip', 'VIP/Unlimited'),
        ],
        default='non_member'
    )
    
    # Add-ons and customization
    addons = models.ManyToManyField(
        'services.ServiceAddon',
        blank=True,
        through='BookingAddon'
    )
    
    # AI and IoT preferences
    ai_program = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Selected AI massage program"
    )
    scene_preferences = models.JSONField(
        default=dict,
        help_text="IoT scene settings (lighting, scent, temperature)"
    )
    
    # Special requests
    special_requests = models.TextField(blank=True)
    allergies_notes = models.TextField(blank=True)
    medical_notes = models.TextField(blank=True, help_text="Staff only")
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    addons_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment tracking
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('partial', 'Partially Paid'),
            ('failed', 'Failed'),
            ('refunded', 'Refunded'),
        ],
        default='pending'
    )
    payment_method = models.CharField(max_length=50, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    
    # Timestamps
    booked_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True)
    
    # Staff assignment
    assigned_technician = models.CharField(max_length=100, blank=True)
    technician_notes = models.TextField(blank=True)
    
    # QuickBooks sync
    quickbooks_synced = models.BooleanField(default=False)
    quickbooks_invoice_id = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'bookings'
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-booking_date', '-start_time']
        indexes = [
            models.Index(fields=['user', 'booking_date']),
            models.Index(fields=['booking_date', 'start_time']),
            models.Index(fields=['status', 'booking_date']),
        ]

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = self.generate_booking_reference()
        
        # Set booking tier based on user membership
        if self.user.is_authenticated:
            if hasattr(self.user, 'membership') and self.user.membership.is_active:
                membership = self.user.membership
                if membership.plan.name.lower() == 'unlimited':
                    self.booking_tier = 'vip'
                    self.is_priority_booking = True
                elif membership.plan.priority_booking:
                    self.booking_tier = 'member_priority'
                    self.is_priority_booking = True
                else:
                    self.booking_tier = 'member_standard'
            else:
                self.booking_tier = 'non_member'
        
        # Calculate end time
        if not self.end_time and self.start_time and self.duration:
            start_datetime = datetime.combine(self.booking_date, self.start_time)
            end_datetime = start_datetime + timedelta(minutes=self.duration)
            self.end_time = end_datetime.time()
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking_reference} - {self.user.full_name} - {self.service.name}"

    def generate_booking_reference(self):
        """Generate unique booking reference."""
        year = timezone.now().year
        # Get last booking number for this year
        last_booking = Booking.objects.filter(
            booking_reference__startswith=f'CS-{year}-'
        ).order_by('-booking_reference').first()
        
        if last_booking:
            # Extract number and increment
            last_num = int(last_booking.booking_reference.split('-')[-1])
            next_num = last_num + 1
        else:
            next_num = 1
            
        return f'CS-{year}-{next_num:06d}'

    def can_cancel(self):
        """Check if booking can be cancelled."""
        if self.status in ['completed', 'cancelled', 'no_show']:
            return False
            
        # Members can cancel up to 24 hours before
        # Non-members up to 48 hours before
        booking_datetime = datetime.combine(self.booking_date, self.start_time)
        now = timezone.now()
        
        if self.booking_tier in ['member_priority', 'member_standard', 'vip']:
            return booking_datetime - now > timedelta(hours=24)
        else:
            return booking_datetime - now > timedelta(hours=48)

    def can_reschedule(self):
        """Check if booking can be rescheduled."""
        return self.can_cancel() and self.status == 'confirmed'

    def get_priority_deadline(self):
        """Get the deadline when non-members can book this slot."""
        if not self.is_priority_booking:
            return None
            
        # Priority deadline is 3 days before the booking
        booking_datetime = datetime.combine(self.booking_date, self.start_time)
        return booking_datetime - timedelta(days=3)

    def calculate_total(self):
        """Calculate final total including addons and discounts."""
        total = self.base_price
        
        # Add addons
        addon_total = sum(
            addon.total_price for addon in self.booking_addons.all()
        )
        total += addon_total
        
        # Apply membership discount
        if hasattr(self.user, 'membership') and self.user.membership.is_active:
            membership = self.user.membership
            discount_percent = membership.plan.discount_percentage
            discount_amount = (total * discount_percent) / 100
            total -= discount_amount
            self.discount_applied = discount_amount
        
        self.addons_total = addon_total
        self.final_total = total
        return total


class BookingAddon(BaseModel):
    """
    Through model for booking add-ons with quantity and customization.
    """
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='booking_addons'
    )
    addon = models.ForeignKey(
        'services.ServiceAddon',
        on_delete=models.CASCADE
    )
    
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Customization options
    notes = models.TextField(blank=True)
    preferences = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'booking_addons'
        verbose_name = 'Booking Add-on'
        verbose_name_plural = 'Booking Add-ons'
        unique_together = ['booking', 'addon']

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking.booking_reference} - {self.addon.name} x{self.quantity}"


class AvailabilitySlot(BaseModel):
    """
    Pre-defined availability slots for booking system.
    Handles priority access for members vs non-members.
    """
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='availability_slots')
    
    # Capacity and booking limits
    max_bookings = models.PositiveIntegerField(default=1)
    current_bookings = models.PositiveIntegerField(default=0)
    
    # Priority access control
    member_only_until = models.DateTimeField(
        help_text="Non-members can book after this date/time"
    )
    vip_only_until = models.DateTimeField(
        blank=True, 
        null=True,
        help_text="VIP/Unlimited members get first access"
    )
    
    # Pricing
    base_price_modifier = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        help_text="Price modifier for this slot (e.g., 1.5 for peak hours)"
    )
    
    # Status
    is_blocked = models.BooleanField(default=False)
    block_reason = models.CharField(max_length=255, blank=True)
    
    # Special designations
    is_premium_slot = models.BooleanField(default=False)
    tags = models.JSONField(
        default=list,
        help_text="Tags like ['peak_hour', 'weekend', 'holiday']"
    )

    class Meta:
        db_table = 'availability_slots'
        verbose_name = 'Availability Slot'
        verbose_name_plural = 'Availability Slots'
        ordering = ['date', 'start_time']
        unique_together = ['date', 'start_time', 'room']
        indexes = [
            models.Index(fields=['date', 'room']),
            models.Index(fields=['member_only_until']),
        ]

    def __str__(self):
        return f"{self.room.name} - {self.date} {self.start_time}-{self.end_time}"

    def is_available_for_user(self, user, check_date_time=None):
        """Check if slot is available for specific user."""
        now = check_date_time or timezone.now()
        
        # Check if slot is blocked
        if self.is_blocked:
            return False
            
        # Check capacity
        if self.current_bookings >= self.max_bookings:
            return False
        
        # Check VIP access
        if self.vip_only_until and now < self.vip_only_until:
            if not (hasattr(user, 'membership') and 
                   user.membership.is_active and 
                   user.membership.plan.name.lower() == 'unlimited'):
                return False
        
        # Check member priority access
        if now < self.member_only_until:
            if not (hasattr(user, 'membership') and user.membership.is_active):
                return False
        
        return True

    def get_price_for_service(self, service, user=None):
        """Calculate price for this slot based on service and user."""
        if user:
            base_price = service.get_price_for_user(user)
        else:
            base_price = service.non_member_price
            
        # Apply room premium
        price = base_price * self.room.premium_modifier
        
        # Apply slot modifier (peak hours, etc.)
        price = price * self.base_price_modifier
        
        return round(price, 2)

    def book_slot(self, user, service, **booking_data):
        """Create a booking for this slot."""
        if not self.is_available_for_user(user):
            raise ValueError("Slot not available for this user")
            
        # Create booking
        booking = Booking.objects.create(
            user=user,
            service=service,
            room=self.room,
            booking_date=self.date,
            start_time=self.start_time,
            end_time=self.end_time,
            duration=service.duration,
            base_price=self.get_price_for_service(service, user),
            **booking_data
        )
        
        # Update slot capacity
        self.current_bookings += 1
        self.save()
        
        return booking
