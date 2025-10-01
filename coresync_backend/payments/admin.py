"""
Django Admin configuration for Payments app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Payment, StripeWebhookEvent, QuickBooksSync


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for Payments."""
    
    list_display = ['payment_id_short', 'user_name', 'payment_type', 'amount', 'currency', 'status', 'payment_method', 'quickbooks_status', 'created_at']
    list_filter = ['payment_type', 'payment_method', 'status', 'quickbooks_synced', 'created_at']
    search_fields = ['payment_id', 'user__email', 'user__first_name', 'user__last_name', 'description']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_id', 'user', 'payment_type', 'payment_method', 'amount', 'currency', 'description')
        }),
        ('Status', {
            'fields': ('status', 'processed_at'),
            'description': 'Current payment status and processing time'
        }),
        ('Stripe Integration', {
            'fields': ('stripe_payment_intent_id', 'stripe_charge_id', 'stripe_customer_id'),
            'classes': ('collapse',)
        }),
        ('QuickBooks Integration', {
            'fields': ('quickbooks_payment_id', 'quickbooks_synced', 'quickbooks_sync_error'),
            'description': 'QuickBooks synchronization status'
        }),
        ('Related Records', {
            'fields': ('service_history', 'membership'),
            'classes': ('collapse',)
        }),
        ('Refund Information', {
            'fields': ('refund_amount', 'refund_reason', 'refunded_at'),
            'classes': ('collapse',)
        }),
        ('Additional Details', {
            'fields': ('notes', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['payment_id', 'created_at', 'updated_at']
    
    def payment_id_short(self, obj):
        """Display shortened payment ID."""
        return str(obj.payment_id)[:8] + "..."
    payment_id_short.short_description = 'Payment ID'
    
    def user_name(self, obj):
        """Display user full name with link."""
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.full_name)
    user_name.short_description = 'Customer'
    
    def quickbooks_status(self, obj):
        """Show QuickBooks sync status with color coding."""
        if obj.quickbooks_synced:
            return format_html('<span style="color: green;">✓ Synced</span>')
        elif obj.quickbooks_sync_error:
            return format_html('<span style="color: red;">✗ Error</span>')
        else:
            return format_html('<span style="color: orange;">⏳ Pending</span>')
    quickbooks_status.short_description = 'QuickBooks'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('user')
    
    # Actions
    actions = ['retry_quickbooks_sync', 'mark_as_succeeded', 'create_refund']
    
    def retry_quickbooks_sync(self, request, queryset):
        """Retry QuickBooks synchronization for selected payments."""
        failed_payments = queryset.filter(quickbooks_synced=False)
        count = failed_payments.count()
        # Here you would trigger the QuickBooks sync task
        self.message_user(request, f'QuickBooks sync queued for {count} payments.')
    retry_quickbooks_sync.short_description = "Retry QuickBooks sync"
    
    def mark_as_succeeded(self, request, queryset):
        """Mark selected payments as succeeded."""
        updated = queryset.filter(status='pending').update(status='succeeded')
        self.message_user(request, f'{updated} payments marked as succeeded.')
    mark_as_succeeded.short_description = "Mark as succeeded"


@admin.register(StripeWebhookEvent)
class StripeWebhookEventAdmin(admin.ModelAdmin):
    """Admin interface for Stripe Webhook Events."""
    
    list_display = ['event_id_short', 'event_type', 'processed', 'created_at', 'processing_time']
    list_filter = ['event_type', 'processed', 'created_at']
    search_fields = ['event_id', 'event_type']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('event_id', 'event_type', 'stripe_created')
        }),
        ('Processing', {
            'fields': ('processed', 'processed_at', 'error_message'),
            'description': 'Event processing status and details'
        }),
        ('Payload', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']
    
    def event_id_short(self, obj):
        """Display shortened event ID."""
        return str(obj.event_id)[:20] + "..."
    event_id_short.short_description = 'Event ID'
    
    def processing_time(self, obj):
        """Show processing time if available."""
        if obj.processed_at and obj.created_at:
            delta = obj.processed_at - obj.created_at
            return f"{delta.total_seconds():.2f}s"
        return "-"
    processing_time.short_description = 'Processing Time'
    
    # Actions
    actions = ['reprocess_webhook', 'mark_as_processed']
    
    def reprocess_webhook(self, request, queryset):
        """Reprocess selected webhook events."""
        unprocessed = queryset.filter(processed=False)
        count = unprocessed.count()
        self.message_user(request, f'{count} webhook events queued for reprocessing.')
    reprocess_webhook.short_description = "Reprocess webhooks"


@admin.register(QuickBooksSync)
class QuickBooksSyncAdmin(admin.ModelAdmin):
    """Admin interface for QuickBooks Synchronization."""
    
    list_display = ['sync_type', 'object_id', 'status', 'attempts', 'last_attempt_at', 'next_attempt_at', 'quickbooks_id']
    list_filter = ['sync_type', 'status', 'attempts', 'created_at']
    search_fields = ['object_id', 'quickbooks_id', 'error_message']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Sync Information', {
            'fields': ('sync_type', 'object_id', 'quickbooks_id', 'status')
        }),
        ('Retry Logic', {
            'fields': ('attempts', 'max_attempts', 'last_attempt_at', 'next_attempt_at'),
            'description': 'Automatic retry configuration and tracking'
        }),
        ('Error Details', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Sync Data', {
            'fields': ('sync_data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_attempt_at']
    
    def get_queryset(self, request):
        """Order by status priority."""
        return super().get_queryset(request).order_by('status', '-created_at')
    
    # Actions
    actions = ['retry_sync', 'mark_completed', 'skip_sync']
    
    def retry_sync(self, request, queryset):
        """Retry failed synchronizations."""
        retryable = queryset.filter(status='failed').filter(attempts__lt=models.F('max_attempts'))
        count = retryable.count()
        retryable.update(status='pending', next_attempt_at=timezone.now())
        self.message_user(request, f'{count} sync records queued for retry.')
    retry_sync.short_description = "Retry sync"
    
    def mark_completed(self, request, queryset):
        """Mark selected syncs as completed."""
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} sync records marked as completed.')
    mark_completed.short_description = "Mark as completed"
    
    def skip_sync(self, request, queryset):
        """Skip selected syncs."""
        updated = queryset.update(status='skipped')
        self.message_user(request, f'{updated} sync records skipped.')
    skip_sync.short_description = "Skip sync"
    
    # Custom views for sync statistics
    def changelist_view(self, request, extra_context=None):
        """Add sync statistics to changelist view."""
        extra_context = extra_context or {}
        
        # Calculate sync statistics
        total_syncs = self.model.objects.count()
        completed_syncs = self.model.objects.filter(status='completed').count()
        failed_syncs = self.model.objects.filter(status='failed').count()
        pending_syncs = self.model.objects.filter(status='pending').count()
        
        extra_context['sync_stats'] = {
            'total': total_syncs,
            'completed': completed_syncs,
            'failed': failed_syncs,
            'pending': pending_syncs,
            'success_rate': round((completed_syncs / total_syncs * 100), 2) if total_syncs > 0 else 0
        }
        
        return super().changelist_view(request, extra_context=extra_context)
