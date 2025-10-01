"""
Django Admin configuration for Users app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin interface for custom User model with membership features.
    """
    list_display = ['email', 'full_name', 'membership_status', 'membership_plan', 'biometric_enabled', 'is_active', 'date_joined']
    list_filter = ['membership_status', 'biometric_enabled', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering = ['-date_joined']
    
    # Custom fieldsets for the admin form
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Membership Information', {
            'fields': ('membership_status', 'membership_plan')
        }),
        ('Contact Information', {
            'fields': ('phone', 'date_of_birth', 'emergency_contact', 'emergency_phone')
        }),
        ('Biometric & Security', {
            'fields': ('biometric_enabled', 'face_recognition_data'),
            'classes': ('collapse',)  # Collapsible section
        }),
        ('Preferences', {
            'fields': ('email_notifications', 'sms_notifications'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Add fields to the add form
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Information', {
            'fields': ('email', 'first_name', 'last_name', 'phone', 'membership_status')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'face_recognition_data']
    
    def full_name(self, obj):
        """Display full name in list view."""
        return obj.full_name
    full_name.short_description = 'Full Name'
    
    def membership_plan(self, obj):
        """Display membership plan with color coding."""
        if obj.membership_plan:
            color = obj.membership_plan.color_scheme if hasattr(obj.membership_plan, 'color_scheme') else '#007cba'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color,
                obj.membership_plan.name
            )
        return '-'
    membership_plan.short_description = 'Membership Plan'
    
    # Advanced filters
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('membership_plan')
    
    # Actions
    actions = ['activate_biometric', 'deactivate_biometric', 'send_welcome_email']
    
    def activate_biometric(self, request, queryset):
        """Enable biometric authentication for selected users."""
        updated = queryset.update(biometric_enabled=True)
        self.message_user(request, f'{updated} users enabled for biometric authentication.')
    activate_biometric.short_description = "Enable biometric authentication"
    
    def deactivate_biometric(self, request, queryset):
        """Disable biometric authentication for selected users."""
        updated = queryset.update(biometric_enabled=False)
        self.message_user(request, f'{updated} users disabled from biometric authentication.')
    deactivate_biometric.short_description = "Disable biometric authentication"
    
    def send_welcome_email(self, request, queryset):
        """Send welcome email to selected users."""
        # This would integrate with your email system
        count = queryset.count()
        self.message_user(request, f'Welcome emails queued for {count} users.')
    send_welcome_email.short_description = "Send welcome email"
