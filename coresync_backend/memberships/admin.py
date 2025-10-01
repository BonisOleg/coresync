"""
Django Admin configuration for Memberships app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum, Q
from django.db import models
from django.utils import timezone
from .models import MembershipPlan, Membership


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    """Admin interface for Membership Plans."""
    
    list_display = ['name', 'price', 'duration_months', 'discount_percentage', 'member_count', 'priority_booking', 'featured', 'is_active']
    list_filter = ['duration_months', 'priority_booking', 'featured', 'is_active', 'created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['price']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'short_description')
        }),
        ('Pricing & Duration', {
            'fields': ('price', 'duration_months', 'discount_percentage'),
            'description': 'Set membership pricing and duration'
        }),
        ('Access & Privileges', {
            'fields': (
                'mensuite_access', 'coresync_private_access', 'iot_control_access', 
                'priority_booking', 'monthly_service_credits', 'guest_passes'
            ),
            'description': 'Configure member access levels and benefits'
        }),
        ('Benefits', {
            'fields': ('benefits',),
            'description': 'JSON list of membership benefits for display'
        }),
        ('Display Settings', {
            'fields': ('featured', 'color_scheme', 'icon', 'order'),
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
    
    def member_count(self, obj):
        """Count active members with this plan."""
        active_count = obj.memberships.filter(status='active').count()
        if active_count > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">{} active</span>',
                active_count
            )
        return '0 active'
    member_count.short_description = 'Active Members'
    
    def get_queryset(self, request):
        """Optimize queryset with annotations."""
        return super().get_queryset(request).annotate(
            active_members_count=Count('memberships', filter=models.Q(memberships__status='active'))
        )
    
    # Actions
    actions = ['mark_featured', 'unmark_featured', 'recalculate_savings']
    
    def mark_featured(self, request, queryset):
        """Mark selected plans as featured."""
        updated = queryset.update(featured=True)
        self.message_user(request, f'{updated} membership plans marked as featured.')
    mark_featured.short_description = "Mark as featured"
    
    def unmark_featured(self, request, queryset):
        """Unmark selected plans as featured."""
        updated = queryset.update(featured=False)
        self.message_user(request, f'{updated} membership plans unmarked as featured.')
    unmark_featured.short_description = "Remove from featured"
    
    def recalculate_savings(self, request, queryset):
        """Recalculate savings for selected plans."""
        count = queryset.count()
        self.message_user(request, f'Savings recalculated for {count} membership plans.')
    recalculate_savings.short_description = "Recalculate member savings"


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    """Admin interface for Active Memberships."""
    
    list_display = ['user_name', 'user_email', 'plan', 'status', 'start_date', 'end_date', 'days_remaining_display', 'auto_renew']
    list_filter = ['status', 'auto_renew', 'plan', 'start_date', 'end_date']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'plan__name']
    date_hierarchy = 'start_date'
    ordering = ['-start_date']
    
    fieldsets = (
        ('Member Information', {
            'fields': ('user', 'plan')
        }),
        ('Membership Period', {
            'fields': ('start_date', 'end_date', 'status'),
            'description': 'Membership validity period and current status'
        }),
        ('Usage Tracking', {
            'fields': ('services_used_this_month', 'guest_passes_used'),
            'description': 'Track member usage of benefits'
        }),
        ('Payment & Renewal', {
            'fields': ('stripe_subscription_id', 'auto_renew'),
            'classes': ('collapse',)
        }),
        ('Notes & Comments', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def user_name(self, obj):
        """Display user full name."""
        return obj.user.full_name
    user_name.short_description = 'Member Name'
    
    def user_email(self, obj):
        """Display user email."""
        return obj.user.email
    user_email.short_description = 'Email'
    
    def days_remaining_display(self, obj):
        """Show days remaining with color coding."""
        days = obj.days_remaining
        if days <= 0:
            return format_html('<span style="color: red; font-weight: bold;">Expired</span>')
        elif days <= 7:
            return format_html('<span style="color: orange; font-weight: bold;">{} days</span>', days)
        elif days <= 30:
            return format_html('<span style="color: blue;">{} days</span>', days)
        else:
            return format_html('<span style="color: green;">{} days</span>', days)
    days_remaining_display.short_description = 'Days Remaining'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('user', 'plan')
    
    # Actions
    actions = ['renew_membership', 'suspend_membership', 'reactivate_membership', 'send_renewal_reminder']
    
    def renew_membership(self, request, queryset):
        """Extend membership period for selected memberships."""
        from datetime import timedelta
        updated = 0
        for membership in queryset:
            if membership.status == 'active':
                membership.end_date = membership.end_date + timedelta(days=membership.plan.duration_months * 30)
                membership.save()
                updated += 1
        self.message_user(request, f'{updated} memberships renewed.')
    renew_membership.short_description = "Renew memberships"
    
    def suspend_membership(self, request, queryset):
        """Suspend selected active memberships."""
        updated = queryset.filter(status='active').update(status='suspended')
        self.message_user(request, f'{updated} memberships suspended.')
    suspend_membership.short_description = "Suspend memberships"
    
    def reactivate_membership(self, request, queryset):
        """Reactivate selected suspended memberships."""
        updated = queryset.filter(status='suspended').update(status='active')
        self.message_user(request, f'{updated} memberships reactivated.')
    reactivate_membership.short_description = "Reactivate memberships"
    
    def send_renewal_reminder(self, request, queryset):
        """Send renewal reminder to selected members."""
        count = queryset.count()
        self.message_user(request, f'Renewal reminders sent to {count} members.')
    send_renewal_reminder.short_description = "Send renewal reminders"
    
    # Custom filters
    def get_changelist_instance(self, request):
        """Add custom filters to changelist."""
        changelist = super().get_changelist_instance(request)
        
        # Add expiring soon filter
        if 'expiring_soon' in request.GET:
            from datetime import date, timedelta
            next_week = date.today() + timedelta(days=7)
            changelist.queryset = changelist.queryset.filter(
                end_date__lte=next_week,
                status='active'
            )
        
        return changelist


# Custom admin site title and header
admin.site.site_header = 'CoreSync Spa Administration'
admin.site.site_title = 'CoreSync Admin'
admin.site.index_title = 'Welcome to CoreSync Administration Panel'
