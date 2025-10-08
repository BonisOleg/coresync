"""Admin configuration for Shop app."""
from django.contrib import admin
from .models import Product, PickupOrder, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'price', 'member_price',
        'stock', 'is_featured', 'is_active'
    ]
    list_filter = ['category', 'is_active', 'is_featured']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description', 'short_description')
        }),
        ('Pricing', {
            'fields': ('price', 'member_price', 'member_discount_percent')
        }),
        ('Inventory', {
            'fields': ('stock', 'low_stock_threshold')
        }),
        ('Media', {
            'fields': ('main_image', 'gallery_images')
        }),
        ('Availability', {
            'fields': ('is_active', 'is_featured')
        }),
        ('QuickBooks', {
            'fields': ('quickbooks_item_id', 'quickbooks_synced'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']
    fields = ['product', 'quantity', 'unit_price', 'total_price', 'notes']


@admin.register(PickupOrder)
class PickupOrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user', 'status',
        'total', 'pickup_date', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'pickup_date']
    search_fields = ['order_number', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status')
        }),
        ('Pickup Details', {
            'fields': ('pickup_date', 'pickup_booking')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax', 'total')
        }),
        ('Payment', {
            'fields': ('payment', 'paid_at')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'staff_notes')
        }),
        ('QuickBooks', {
            'fields': ('quickbooks_synced', 'quickbooks_invoice_id', 'quickbooks_sync_error'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
