"""Admin configuration for Concierge app."""
from django.contrib import admin
from .models import ConciergeRequest


@admin.register(ConciergeRequest)
class ConciergeRequestAdmin(admin.ModelAdmin):
    list_display = [
        'request_number', 'user', 'title',
        'request_type', 'status', 'actual_cost',
        'preferred_pickup_date', 'submitted_at'
    ]
    list_filter = [
        'status', 'request_type', 'requires_age_verification',
        'submitted_at', 'preferred_pickup_date'
    ]
    search_fields = [
        'request_number', 'title', 'description',
        'user__email', 'user__first_name', 'user__last_name'
    ]
    readonly_fields = [
        'request_number', 'submitted_at',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Request Information', {
            'fields': ('request_number', 'user', 'request_type', 'status')
        }),
        ('Details', {
            'fields': ('title', 'description', 'product_link', 'attachments')
        }),
        ('Budget', {
            'fields': ('budget_min', 'budget_max', 'actual_cost')
        }),
        ('Scheduling', {
            'fields': ('preferred_pickup_date', 'pickup_booking')
        }),
        ('Verification', {
            'fields': ('requires_age_verification', 'age_verified')
        }),
        ('Staff Management', {
            'fields': ('admin_notes', 'decline_reason', 'reviewed_at', 'completed_at')
        }),
        ('Payment', {
            'fields': ('payment', 'paid_at')
        }),
        ('QuickBooks', {
            'fields': ('quickbooks_synced', 'quickbooks_invoice_id', 'quickbooks_sync_error'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('submitted_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_requests', 'mark_as_processing', 'mark_as_ready']
    
    def approve_requests(self, request, queryset):
        """Approve selected requests."""
        updated = queryset.filter(status='pending').update(
            status='approved',
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{updated} requests approved.')
    approve_requests.short_description = 'Approve selected requests'
    
    def mark_as_processing(self, request, queryset):
        """Mark requests as processing."""
        updated = queryset.filter(status='approved').update(status='processing')
        self.message_user(request, f'{updated} requests marked as processing.')
    mark_as_processing.short_description = 'Mark as processing'
    
    def mark_as_ready(self, request, queryset):
        """Mark requests as ready for pickup."""
        from django.utils import timezone
        updated = queryset.filter(status='processing').update(
            status='ready',
            completed_at=timezone.now()
        )
        self.message_user(request, f'{updated} requests marked as ready.')
    mark_as_ready.short_description = 'Mark as ready for pickup'
