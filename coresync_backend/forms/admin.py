"""
Django Admin configuration for Forms app.
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
    actions = ['mark_as_responded', 'assign_to_me', 'mark_as_spam', 'export_to_csv']
    
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
    
    list_display = ['name', 'email', 'phone', 'interested_plan', 'status', 'follow_up_date', 'created_at']
    list_filter = ['interested_plan', 'status', 'follow_up_date', 'created_at']
    search_fields = ['name', 'email', 'phone', 'interested_plan']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Inquiry Information', {
            'fields': ('name', 'email', 'phone', 'interested_plan', 'message')
        }),
        ('Status & Follow-up', {
            'fields': ('status', 'follow_up_date', 'sales_notes'),
            'description': 'Sales tracking and follow-up scheduling'
        }),
        ('Conversion Tracking', {
            'fields': ('converted_to_member', 'conversion_date', 'membership_plan_purchased'),
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
    
    readonly_fields = ['created_at', 'updated_at', 'conversion_date']
    
    def get_queryset(self, request):
        """Order by follow-up priority."""
        return super().get_queryset(request).order_by('follow_up_date', '-created_at')
    
    # Actions
    actions = ['schedule_follow_up', 'mark_converted', 'send_membership_info']
    
    def schedule_follow_up(self, request, queryset):
        """Schedule follow-up for selected inquiries."""
        from datetime import date
        follow_up_date = date.today() + timedelta(days=3)
        updated = queryset.update(
            follow_up_date=follow_up_date,
            status='follow_up_scheduled'
        )
        self.message_user(request, f'{updated} inquiries scheduled for follow-up on {follow_up_date}.')
    schedule_follow_up.short_description = "Schedule 3-day follow-up"
    
    def mark_converted(self, request, queryset):
        """Mark selected inquiries as converted to memberships."""
        updated = queryset.update(
            converted_to_member=True,
            conversion_date=timezone.now().date(),
            status='converted'
        )
        self.message_user(request, f'{updated} inquiries marked as converted.')
    mark_converted.short_description = "Mark as converted"


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for Newsletter Subscriptions."""
    
    list_display = ['email', 'name', 'subscribed', 'email_verified', 'source', 'created_at']
    list_filter = ['subscribed', 'email_verified', 'source', 'created_at']
    search_fields = ['email', 'name']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Subscriber Information', {
            'fields': ('email', 'name', 'phone')
        }),
        ('Subscription Status', {
            'fields': ('subscribed', 'email_verified', 'verification_token'),
            'description': 'Current subscription and verification status'
        }),
        ('Subscription Details', {
            'fields': ('source', 'interests', 'preferred_frequency'),
            'classes': ('collapse',)
        }),
        ('Tracking', {
            'fields': ('subscribed_at', 'unsubscribed_at', 'last_email_sent'),
            'classes': ('collapse',)
        }),
        ('Technical Details', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['verification_token', 'created_at', 'updated_at', 'subscribed_at', 'unsubscribed_at']
    
    def get_queryset(self, request):
        """Show active subscriptions first."""
        return super().get_queryset(request).order_by('-subscribed', '-created_at')
    
    # Actions
    actions = ['send_verification_email', 'mark_as_verified', 'unsubscribe_selected', 'export_subscriber_list']
    
    def send_verification_email(self, request, queryset):
        """Send verification emails to unverified subscribers."""
        unverified = queryset.filter(email_verified=False)
        count = unverified.count()
        self.message_user(request, f'Verification emails sent to {count} subscribers.')
    send_verification_email.short_description = "Send verification emails"
    
    def mark_as_verified(self, request, queryset):
        """Mark selected subscriptions as email verified."""
        updated = queryset.update(email_verified=True)
        self.message_user(request, f'{updated} subscriptions marked as verified.')
    mark_as_verified.short_description = "Mark as verified"
    
    def unsubscribe_selected(self, request, queryset):
        """Unsubscribe selected subscribers."""
        updated = queryset.update(
            subscribed=False,
            unsubscribed_at=timezone.now()
        )
        self.message_user(request, f'{updated} subscribers unsubscribed.')
    unsubscribe_selected.short_description = "Unsubscribe"
    
    # Custom dashboard metrics
    def changelist_view(self, request, extra_context=None):
        """Add subscription statistics to changelist view."""
        extra_context = extra_context or {}
        
        # Calculate subscription statistics
        total_subscribers = self.model.objects.count()
        active_subscribers = self.model.objects.filter(subscribed=True).count()
        verified_subscribers = self.model.objects.filter(email_verified=True).count()
        recent_subscribers = self.model.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        extra_context['subscription_stats'] = {
            'total': total_subscribers,
            'active': active_subscribers,
            'verified': verified_subscribers,
            'recent': recent_subscribers,
            'verification_rate': round((verified_subscribers / total_subscribers * 100), 2) if total_subscribers > 0 else 0
        }
        
        return super().changelist_view(request, extra_context=extra_context)
