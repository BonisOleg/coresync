"""
Django Admin configuration for Services app.
FIXED: All fields match actual models from booking_models.py
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import ServiceCategory, Service, ServiceAddon, ServiceHistory
from .booking_models import Room, Booking, BookingAddon, AvailabilitySlot


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    """Admin interface for Service Categories."""
    
    list_display = ['name', 'slug', 'service_count', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'image', 'order')
        }),
        ('Features', {
            'fields': ('featured_technologies',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def service_count(self, obj):
        """Count services in this category."""
        return obj.services.count()
    service_count.short_description = 'Services Count'
    
    def get_queryset(self, request):
        """Optimize queryset with annotations."""
        return super().get_queryset(request).annotate(
            services_count=Count('services')
        )


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Admin interface for Services."""
    
    list_display = ['name', 'category', 'member_price', 'non_member_price', 'duration', 'member_discount', 'featured', 'is_active']
    list_filter = ['category', 'duration', 'featured', 'member_only', 'is_active', 'created_at']
    search_fields = ['name', 'slug', 'description', 'category__name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['category', 'order', 'name']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'description', 'short_description')
        }),
        ('Pricing', {
            'fields': ('member_price', 'non_member_price'),
            'description': 'Set different prices for members and non-members'
        }),
        ('Logistics', {
            'fields': ('duration', 'max_capacity', 'requires_appointment', 'member_only'),
        }),
        ('Media', {
            'fields': ('main_image', 'gallery_images', 'video_url'),
            'classes': ('collapse',)
        }),
        ('SEO & Display', {
            'fields': ('meta_title', 'meta_description', 'featured', 'order'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def member_discount(self, obj):
        """Show member discount percentage."""
        discount = obj.member_discount_percentage
        if discount > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">{}%</span>',
                discount
            )
        return '0%'
    member_discount.short_description = 'Member Discount'
    
    # Actions
    actions = ['mark_featured', 'unmark_featured']
    
    def mark_featured(self, request, queryset):
        """Mark selected services as featured."""
        updated = queryset.update(featured=True)
        self.message_user(request, f'{updated} services marked as featured.')
    mark_featured.short_description = "Mark as featured"
    
    def unmark_featured(self, request, queryset):
        """Unmark selected services as featured."""
        updated = queryset.update(featured=False)
        self.message_user(request, f'{updated} services unmarked as featured.')
    unmark_featured.short_description = "Remove from featured"


@admin.register(ServiceAddon)
class ServiceAddonAdmin(admin.ModelAdmin):
    """Admin interface for Service Add-ons."""
    
    list_display = ['name', 'price', 'available_for_all_services', 'applicable_services_count', 'is_active']
    list_filter = ['available_for_all_services', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['services']
    ordering = ['name']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'price')
        }),
        ('Availability', {
            'fields': ('available_for_all_services', 'services'),
            'description': 'Select specific services or make available for all services'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def applicable_services_count(self, obj):
        """Count applicable services."""
        if obj.available_for_all_services:
            return "All Services"
        return obj.services.count()
    applicable_services_count.short_description = 'Applicable Services'


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """Admin interface for Spa Rooms."""
    
    list_display = ['name', 'room_type', 'capacity', 'maintenance_mode', 'has_iot_control', 'is_active']
    list_filter = ['room_type', 'maintenance_mode', 'has_iot_control', 'is_active', 'created_at']
    search_fields = ['name', 'features']
    ordering = ['room_type', 'name']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'room_type', 'capacity')
        }),
        ('Features', {
            'fields': ('features',),
            'description': 'JSON list of room features',
            'classes': ('collapse',)
        }),
        ('IoT Integration', {
            'fields': ('has_iot_control', 'iot_device_ids'),
            'classes': ('collapse',)
        }),
        ('Operating Hours', {
            'fields': ('opening_time', 'closing_time'),
        }),
        ('Pricing', {
            'fields': ('premium_modifier',),
            'description': 'Price multiplier for this room (1.0 = standard)'
        }),
        ('Status', {
            'fields': ('is_active', 'maintenance_mode')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin interface for Bookings."""
    
    list_display = ['booking_reference', 'user_name', 'service', 'room', 'booking_date', 'start_time', 'status', 'payment_status']
    list_filter = ['status', 'payment_status', 'booking_tier', 'booking_date', 'created_at']
    search_fields = ['booking_reference', 'user__email', 'user__first_name', 'user__last_name', 'service__name']
    date_hierarchy = 'booking_date'
    ordering = ['-booking_date', '-start_time']
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_reference', 'user', 'service', 'room')
        }),
        ('Schedule', {
            'fields': ('booking_date', 'start_time', 'end_time', 'duration')
        }),
        ('Guest Information', {
            'fields': ('guest_name', 'guest_phone', 'guest_email'),
            'classes': ('collapse',)
        }),
        ('Pricing', {
            'fields': ('base_price', 'addons_total', 'discount_applied', 'final_total', 'booking_tier')
        }),
        ('Payment', {
            'fields': ('payment_status', 'payment_method', 'stripe_payment_intent_id')
        }),
        ('Status', {
            'fields': ('status', 'is_priority_booking', 'booked_at', 'confirmed_at')
        }),
        ('Service Details', {
            'fields': ('assigned_technician', 'ai_program', 'scene_preferences'),
            'classes': ('collapse',)
        }),
        ('Special Requests', {
            'fields': ('special_requests', 'allergies_notes', 'medical_notes'),
            'classes': ('collapse',)
        }),
        ('Cancellation', {
            'fields': ('cancelled_at', 'cancellation_reason'),
            'classes': ('collapse',)
        }),
        ('QuickBooks', {
            'fields': ('quickbooks_synced', 'quickbooks_invoice_id'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['booking_reference', 'created_at', 'updated_at', 'booked_at', 'confirmed_at', 'cancelled_at', 'addons_total', 'final_total']
    
    def user_name(self, obj):
        """Display user full name."""
        return obj.user.full_name
    user_name.short_description = 'Customer'
    
    # Actions
    actions = ['confirm_booking', 'cancel_booking']
    
    def confirm_booking(self, request, queryset):
        """Confirm selected bookings."""
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(status='confirmed', confirmed_at=timezone.now())
        self.message_user(request, f'{updated} bookings confirmed.')
    confirm_booking.short_description = "Confirm bookings"
    
    def cancel_booking(self, request, queryset):
        """Cancel selected bookings."""
        from django.utils import timezone
        updated = queryset.filter(status__in=['pending', 'confirmed']).update(
            status='cancelled',
            cancelled_at=timezone.now(),
            cancellation_reason='Cancelled by admin'
        )
        self.message_user(request, f'{updated} bookings cancelled.')
    cancel_booking.short_description = "Cancel bookings"


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    """Admin interface for Availability Slots."""
    
    list_display = ['date', 'start_time', 'end_time', 'room', 'current_bookings', 'max_bookings', 'is_blocked']
    list_filter = ['is_blocked', 'is_premium_slot', 'date', 'room']
    search_fields = ['room__name', 'block_reason']
    date_hierarchy = 'date'
    ordering = ['date', 'start_time']
    
    fieldsets = (
        ('Schedule', {
            'fields': ('date', 'start_time', 'end_time', 'room')
        }),
        ('Capacity', {
            'fields': ('max_bookings', 'current_bookings')
        }),
        ('Priority Access', {
            'fields': ('member_only_until', 'vip_only_until'),
            'description': 'Control when members vs non-members can book'
        }),
        ('Pricing', {
            'fields': ('base_price_modifier',),
            'description': 'Price multiplier for peak hours (1.0 = standard)'
        }),
        ('Status', {
            'fields': ('is_blocked', 'block_reason', 'is_premium_slot', 'tags')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'current_bookings']


# Inline admin for related models
class BookingAddonInline(admin.TabularInline):
    """Inline admin for booking add-ons."""
    model = BookingAddon
    extra = 0
    readonly_fields = ['total_price']
    fields = ['addon', 'quantity', 'unit_price', 'total_price', 'notes']


# Add inline to BookingAdmin
BookingAdmin.inlines = [BookingAddonInline]