"""
Django Admin configuration for Services app.
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
    actions = ['mark_featured', 'unmark_featured', 'enable_member_only']
    
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
    
    list_display = ['name', 'room_type', 'capacity', 'is_available', 'iot_device_connected', 'is_active']
    list_filter = ['room_type', 'is_available', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'iot_device_id']
    ordering = ['name']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'room_type', 'description', 'capacity')
        }),
        ('IoT Integration', {
            'fields': ('iot_device_id', 'iot_capabilities'),
            'classes': ('collapse',)
        }),
        ('Availability', {
            'fields': ('is_available', 'maintenance_notes')
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
    
    def iot_device_connected(self, obj):
        """Show IoT device connection status."""
        if obj.iot_device_id:
            return format_html('<span style="color: green;">✓ Connected</span>')
        return format_html('<span style="color: red;">✗ Not Connected</span>')
    iot_device_connected.short_description = 'IoT Status'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin interface for Bookings."""
    
    list_display = ['booking_reference', 'user_name', 'service', 'room', 'booking_date', 'booking_time', 'status', 'payment_status']
    list_filter = ['status', 'payment_status', 'booking_tier', 'booking_date', 'created_at']
    search_fields = ['booking_reference', 'user__email', 'user__first_name', 'user__last_name', 'service__name']
    date_hierarchy = 'booking_date'
    ordering = ['-booking_date', '-booking_time']
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_reference', 'user', 'service', 'room')
        }),
        ('Schedule', {
            'fields': ('booking_date', 'booking_time', 'duration_minutes')
        }),
        ('Pricing', {
            'fields': ('base_price', 'addon_total', 'discount_amount', 'final_total', 'booking_tier')
        }),
        ('Status', {
            'fields': ('status', 'payment_status', 'stripe_payment_intent_id')
        }),
        ('Additional Information', {
            'fields': ('special_requests', 'scene_preferences', 'notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['booking_reference', 'created_at', 'updated_at', 'addon_total', 'final_total']
    
    def user_name(self, obj):
        """Display user full name."""
        return obj.user.full_name
    user_name.short_description = 'Customer'
    
    # Actions
    actions = ['confirm_booking', 'cancel_booking', 'mark_completed']
    
    def confirm_booking(self, request, queryset):
        """Confirm selected bookings."""
        updated = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(request, f'{updated} bookings confirmed.')
    confirm_booking.short_description = "Confirm bookings"


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    """Admin interface for Availability Slots."""
    
    list_display = ['date', 'start_time', 'end_time', 'room', 'service', 'is_available', 'is_member_only', 'is_priority_slot']
    list_filter = ['is_available', 'is_member_only', 'is_priority_slot', 'date', 'room', 'service']
    search_fields = ['room__name', 'service__name']
    date_hierarchy = 'date'
    ordering = ['date', 'start_time']
    
    fieldsets = (
        ('Schedule', {
            'fields': ('date', 'start_time', 'end_time')
        }),
        ('Assignment', {
            'fields': ('room', 'service')
        }),
        ('Availability', {
            'fields': ('is_available', 'is_member_only', 'is_priority_slot', 'max_bookings', 'current_bookings')
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
    readonly_fields = ['addon_price']


class ServiceHistoryInline(admin.TabularInline):
    """Inline admin for service history."""
    model = ServiceHistory
    extra = 0
    readonly_fields = ['used_at', 'price_paid']


# Add inlines to existing admin
BookingAdmin.inlines = [BookingAddonInline]
