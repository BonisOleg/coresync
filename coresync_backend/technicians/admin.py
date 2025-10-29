"""
Technicians Admin Configuration.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Technician, WorkLog, Schedule


@admin.register(Technician)
class TechnicianAdmin(admin.ModelAdmin):
    list_display = [
        'full_name',
        'email',
        'specialties_display',
        'hourly_rate',
        'is_active_badge',
        'hired_date',
        'weekly_hours'
    ]
    list_filter = ['is_active', 'specialties', 'hired_date']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'weekly_hours']
    
    fieldsets = (
        ('User Info', {
            'fields': ('user', 'is_active')
        }),
        ('Professional Info', {
            'fields': ('specialties', 'hourly_rate', 'hired_date', 'certification_number')
        }),
        ('Contact', {
            'fields': ('phone', 'bio')
        }),
        ('Google Sheets Sync', {
            'fields': ('google_sheet_row_id',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def specialties_display(self, obj):
        if obj.specialties:
            return ', '.join(obj.specialties)
        return '—'
    specialties_display.short_description = 'Specialties'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">✅ Active</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">❌ Inactive</span>'
        )
    is_active_badge.short_description = 'Status'
    
    def weekly_hours(self, obj):
        week_start = timezone.now().date() - timezone.timedelta(
            days=timezone.now().weekday()
        )
        total = obj.get_weekly_hours_total(week_start)
        return f"{total}h"
    weekly_hours.short_description = 'This Week'


@admin.register(WorkLog)
class WorkLogAdmin(admin.ModelAdmin):
    list_display = [
        'technician',
        'date',
        'hours',
        'approved_badge',
        'synced_badge',
        'approved_by',
        'created_at'
    ]
    list_filter = ['approved', 'synced_to_sheets', 'date', 'technician']
    search_fields = ['technician__user__first_name', 'technician__user__last_name', 'notes']
    readonly_fields = ['approved_at', 'synced_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Work Details', {
            'fields': ('technician', 'date', 'hours', 'notes')
        }),
        ('Approval', {
            'fields': ('approved', 'approved_by', 'approved_at')
        }),
        ('Sync Status', {
            'fields': ('synced_to_sheets', 'synced_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['approve_worklogs', 'sync_to_sheets']
    
    def approved_badge(self, obj):
        if obj.approved:
            return format_html(
                '<span style="color: green;">✅ Approved</span>'
            )
        return format_html(
            '<span style="color: orange;">⏳ Pending</span>'
        )
    approved_badge.short_description = 'Approval'
    
    def synced_badge(self, obj):
        if obj.synced_to_sheets:
            return format_html(
                '<span style="color: blue;">☁️ Synced</span>'
            )
        return format_html(
            '<span style="color: gray;">⏳ Not Synced</span>'
        )
    synced_badge.short_description = 'Sync'
    
    def approve_worklogs(self, request, queryset):
        """Bulk approve worklogs."""
        for worklog in queryset:
            worklog.approve(request.user)
        self.message_user(request, f"{queryset.count()} worklogs approved")
    approve_worklogs.short_description = "Approve selected worklogs"
    
    def sync_to_sheets(self, request, queryset):
        """Trigger Google Sheets sync."""
        # TODO: Implement після Google Sheets setup
        self.message_user(request, "Sync queued (TODO: implement)")
    sync_to_sheets.short_description = "Sync to Google Sheets"


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'technician',
        'schedule_type',
        'day_or_date',
        'time_range',
        'is_active_badge'
    ]
    list_filter = ['is_active', 'is_recurring', 'weekday', 'technician']
    search_fields = ['technician__user__first_name', 'technician__user__last_name', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Technician', {
            'fields': ('technician',)
        }),
        ('Schedule Type', {
            'fields': ('is_recurring', 'weekday', 'specific_date')
        }),
        ('Time', {
            'fields': ('start_time', 'end_time')
        }),
        ('Status', {
            'fields': ('is_active', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def schedule_type(self, obj):
        return "Recurring" if obj.is_recurring else "One-time"
    schedule_type.short_description = 'Type'
    
    def day_or_date(self, obj):
        if obj.is_recurring:
            return dict(Schedule.WEEKDAY_CHOICES)[obj.weekday]
        return obj.specific_date
    day_or_date.short_description = 'Day/Date'
    
    def time_range(self, obj):
        return f"{obj.start_time.strftime('%H:%M')} - {obj.end_time.strftime('%H:%M')}"
    time_range.short_description = 'Time'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✅</span>')
        return format_html('<span style="color: red;">❌</span>')
    is_active_badge.short_description = 'Active'
