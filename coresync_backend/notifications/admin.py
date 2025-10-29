"""
Notifications Admin Configuration.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import EmailLog, NotificationPreference


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'email_type_badge',
        'recipient_email',
        'subject_preview',
        'status_badge',
        'sent_at',
        'retry_count'
    ]
    list_filter = ['status', 'email_type', 'sent_at']
    search_fields = ['recipient_email', 'subject', 'sendgrid_message_id']
    readonly_fields = ['created_at', 'sent_at', 'opened_at', 'clicked_at']
    
    fieldsets = (
        ('Recipient', {
            'fields': ('recipient_email', 'recipient_name')
        }),
        ('Email Details', {
            'fields': ('email_type', 'subject', 'booking')
        }),
        ('Status', {
            'fields': ('status', 'sent_at', 'opened_at', 'clicked_at')
        }),
        ('Tracking', {
            'fields': ('sendgrid_message_id', 'retry_count', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    
    def email_type_badge(self, obj):
        colors = {
            'booking_confirmation': '#28a745',
            'booking_reminder': '#ffc107',
            'review_request': '#17a2b8',
            'membership_welcome': '#6f42c1',
            'password_reset': '#6c757d',
            'payment_receipt': '#007bff',
            'cancellation': '#dc3545',
        }
        color = colors.get(obj.email_type, '#6c757d')
        return format_html(
            '<span style="padding: 3px 8px; border-radius: 3px; '
            'background: {}; color: white; font-size: 11px;">{}</span>',
            color, obj.get_email_type_display()
        )
    email_type_badge.short_description = 'Type'
    
    def subject_preview(self, obj):
        preview = obj.subject[:50]
        return f"{preview}..." if len(obj.subject) > 50 else preview
    subject_preview.short_description = 'Subject'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'sent': '#28a745',
            'failed': '#dc3545',
            'bounced': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="padding: 3px 8px; border-radius: 3px; '
            'background: {}; color: white; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'email_enabled',
        'email_booking_confirmations',
        'email_reminders',
        'email_review_requests',
        'email_marketing',
        'updated_at'
    ]
    list_filter = [
        'email_enabled',
        'email_booking_confirmations',
        'email_reminders',
        'email_review_requests',
        'email_marketing'
    ]
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Email Preferences', {
            'fields': (
                'email_enabled',
                'email_booking_confirmations',
                'email_reminders',
                'email_review_requests',
                'email_marketing'
            )
        }),
        ('SMS Preferences (Phase 2)', {
            'fields': ('sms_enabled', 'sms_phone'),
            'classes': ('collapse',)
        }),
        ('Push Notifications (Phase 2)', {
            'fields': ('push_enabled',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('updated_at',)
        }),
    )
