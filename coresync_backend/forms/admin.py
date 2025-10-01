"""
Django Admin configuration for Forms app.
FIXED: All fields match actual models
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import ContactSubmission, MembershipInquiry, NewsletterSubscription


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    """Admin interface for Contact Form Submissions."""
    
    list_display = ['name', 'email', 'phone', 'status', 'assigned_to', 'created_at', 'response_time']
    list_filter = ['status', 'assigned_to', 'created_at', 'responded_at']
    search_fields = ['name', 'email', 'phone', 'message']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone', 'message')
        }),
        ('Status & Assignment', {
            'fields': ('status', 'assigned_to'),
            'description': 'Current status and staff assignment'
        }),
        ('Response Tracking', {
            'fields': ('responded_at', 'response_notes'),
            'classes': ('collapse',)
        }),
        ('Technical Details', {
            'fields': ('ip_address', 'user_agent', 'referrer'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'ip_address', 'user_agent', 'referrer']
    
    def response_time(self, obj):
        """Show response time if responded."""
        if obj.responded_at:
            delta = obj.responded_at - obj.created_at
            hours = delta.total_seconds() / 3600
            if hours < 24:
                return f"{hours:.1f} hours"
            else:
                return f"{hours/24:.1f} days"
        else:
            # Show how long it's been since submission
            delta = timezone.now() - obj.created_at
            hours = delta.total_seconds() / 3600
            if hours < 24:
                return format_html('<span style="color: orange;">{:.1f} hours ago</span>', hours)
            else:
                return format_html('<span style="color: red;">{:.1f} days ago</span>', hours/24)
    response_time.short_description = 'Response Time'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('assigned_to')
    
    # Actions
    actions = ['mark_as_responded', 'assign_to_me', 'mark_as_spam']
    
    def mark_as_responded(self, request, queryset):
        """Mark selected submissions as responded."""
        updated = queryset.update(
            status='responded',
            responded_at=timezone.now()
        )
        self.message_user(request, f'{updated} submissions marked as responded.')
    mark_as_responded.short_description = "Mark as responded"
    
    def assign_to_me(self, request, queryset):
        """Assign selected submissions to current user."""
        updated = queryset.update(
            assigned_to=request.user,
            status='in_progress'
        )
        self.message_user(request, f'{updated} submissions assigned to you.')
    assign_to_me.short_description = "Assign to me"
    
    def mark_as_spam(self, request, queryset):
        """Mark selected submissions as spam."""
        updated = queryset.update(status='spam')
        self.message_user(request, f'{updated} submissions marked as spam.')
    mark_as_spam.short_description = "Mark as spam"


@admin.register(MembershipInquiry)
class MembershipInquiryAdmin(admin.ModelAdmin):
    """Admin interface for Membership Inquiries."""
    
    list_display = ['full_name', 'email', 'phone', 'interested_plan', 'status', 'created_at']
    list_filter = ['interested_plan', 'status', 'interest_level', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'interested_plan']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Membership Interest', {
            'fields': ('interested_plan', 'interest_level', 'preferred_services')
        }),
        ('Preferences', {
            'fields': ('preferred_contact_time', 'how_heard_about_us'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('questions', 'special_requests'),
            'classes': ('collapse',)
        }),
        ('Lead Management', {
            'fields': ('status', 'assigned_to', 'contact_attempts'),
            'description': 'Sales tracking and assignment'
        }),
        ('Follow-up', {
            'fields': ('last_contact_date', 'next_follow_up_date'),
            'classes': ('collapse',)
        }),
        ('Conversion Tracking', {
            'fields': ('converted_user', 'converted_at'),
            'classes': ('collapse',)
        }),
        ('Technical Details', {
            'fields': ('ip_address', 'user_agent', 'utm_source', 'utm_campaign'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'converted_at']
    
    def full_name(self, obj):
        """Display full name."""
        return obj.full_name
    full_name.short_description = 'Name'
    
    def get_queryset(self, request):
        """Order by follow-up priority."""
        return super().get_queryset(request).order_by('next_follow_up_date', '-created_at')
    
    # Actions
    actions = ['schedule_follow_up', 'mark_converted']
    
    def schedule_follow_up(self, request, queryset):
        """Schedule follow-up for selected inquiries."""
        from datetime import datetime
        follow_up_date = datetime.now() + timedelta(days=3)
        updated = queryset.update(
            next_follow_up_date=follow_up_date,
            status='contacted'
        )
        self.message_user(request, f'{updated} inquiries scheduled for follow-up on {follow_up_date.date()}.')
    schedule_follow_up.short_description = "Schedule 3-day follow-up"
    
    def mark_converted(self, request, queryset):
        """Mark selected inquiries as converted to memberships."""
        updated = queryset.update(
            status='converted',
            converted_at=timezone.now()
        )
        self.message_user(request, f'{updated} inquiries marked as converted.')
    mark_converted.short_description = "Mark as converted"


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for Newsletter Subscriptions."""
    
    list_display = ['email', 'first_name', 'is_subscribed', 'source', 'created_at']
    list_filter = ['is_subscribed', 'marketing_emails', 'service_updates', 'source', 'created_at']
    search_fields = ['email', 'first_name']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Subscriber Information', {
            'fields': ('email', 'first_name')
        }),
        ('Subscription Preferences', {
            'fields': ('marketing_emails', 'service_updates', 'special_offers', 'event_notifications'),
            'description': 'Email preferences for subscriber'
        }),
        ('Status', {
            'fields': ('is_subscribed', 'unsubscribed_at', 'unsubscribe_reason'),
            'description': 'Current subscription status'
        }),
        ('Source', {
            'fields': ('source', 'ip_address'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'unsubscribed_at']
    
    def get_queryset(self, request):
        """Show active subscriptions first."""
        return super().get_queryset(request).order_by('-is_subscribed', '-created_at')
    
    # Actions
    actions = ['mark_as_subscribed', 'unsubscribe_selected']
    
    def mark_as_subscribed(self, request, queryset):
        """Re-subscribe selected subscriptions."""
        updated = queryset.update(is_subscribed=True, unsubscribed_at=None)
        self.message_user(request, f'{updated} subscriptions reactivated.')
    mark_as_subscribed.short_description = "Reactivate subscription"
    
    def unsubscribe_selected(self, request, queryset):
        """Unsubscribe selected subscribers."""
        updated = queryset.update(
            is_subscribed=False,
            unsubscribed_at=timezone.now()
        )
        self.message_user(request, f'{updated} subscribers unsubscribed.')
    unsubscribe_selected.short_description = "Unsubscribe"