"""
Django Admin configuration for IoT Control app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from django.utils import timezone
from .models import IoTDevice, Scene, ControlLog, SensorReading


@admin.register(IoTDevice)
class IoTDeviceAdmin(admin.ModelAdmin):
    """Admin interface for IoT Devices."""
    
    list_display = ['name', 'device_type', 'location', 'connection_status', 'last_seen', 'firmware_version', 'is_active']
    list_filter = ['device_type', 'location', 'is_online', 'supports_dimming', 'supports_color', 'is_active']
    search_fields = ['name', 'device_id', 'manufacturer', 'model', 'ip_address']
    ordering = ['location', 'device_type', 'name']
    
    fieldsets = (
        ('Device Information', {
            'fields': ('name', 'device_type', 'location', 'device_id')
        }),
        ('Hardware Details', {
            'fields': ('manufacturer', 'model', 'firmware_version'),
            'classes': ('collapse',)
        }),
        ('Network Configuration', {
            'fields': ('ip_address', 'mac_address', 'wifi_ssid'),
            'classes': ('collapse',)
        }),
        ('Capabilities', {
            'fields': ('supports_dimming', 'supports_color', 'supports_temperature', 'min_value', 'max_value'),
            'description': 'Device feature support and value ranges'
        }),
        ('Status & Connection', {
            'fields': ('is_online', 'last_seen', 'last_command_at', 'error_count')
        }),
        ('Current State', {
            'fields': ('current_value', 'current_color', 'current_temperature'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_seen', 'last_command_at']
    
    def connection_status(self, obj):
        """Show connection status with color coding."""
        if obj.is_online:
            return format_html('<span style="color: green;">🟢 Online</span>')
        else:
            # Check if device was seen recently
            if obj.last_seen:
                delta = timezone.now() - obj.last_seen
                if delta.total_seconds() < 300:  # 5 minutes
                    return format_html('<span style="color: orange;">🟡 Recently Offline</span>')
            return format_html('<span style="color: red;">🔴 Offline</span>')
    connection_status.short_description = 'Status'
    
    def get_queryset(self, request):
        """Order by connection status."""
        return super().get_queryset(request).order_by('-is_online', 'location', 'name')
    
    # Actions
    actions = ['ping_devices', 'restart_devices', 'update_firmware', 'reset_error_count']
    
    def ping_devices(self, request, queryset):
        """Send ping command to selected devices."""
        count = queryset.count()
        self.message_user(request, f'Ping command sent to {count} devices.')
    ping_devices.short_description = "Ping devices"
    
    def restart_devices(self, request, queryset):
        """Restart selected devices."""
        online_devices = queryset.filter(is_online=True)
        count = online_devices.count()
        self.message_user(request, f'Restart command sent to {count} online devices.')
    restart_devices.short_description = "Restart devices"
    
    def reset_error_count(self, request, queryset):
        """Reset error count for selected devices."""
        updated = queryset.update(error_count=0)
        self.message_user(request, f'Error count reset for {updated} devices.')
    reset_error_count.short_description = "Reset error count"


@admin.register(Scene)
class SceneAdmin(admin.ModelAdmin):
    """Admin interface for IoT Scenes."""
    
    list_display = ['name', 'scene_type', 'user', 'device_count', 'is_public', 'usage_count', 'is_active']
    list_filter = ['scene_type', 'is_public', 'is_active', 'location', 'created_at']
    search_fields = ['name', 'description', 'user__username']
    ordering = ['scene_type', 'name']
    
    fieldsets = (
        ('Scene Information', {
            'fields': ('name', 'description', 'scene_type')
        }),
        ('Access Control', {
            'fields': ('user', 'is_public', 'location'),
            'description': 'Scene ownership and location restrictions'
        }),
        ('Device Settings', {
            'fields': ('device_settings',),
            'description': 'JSON configuration for devices in this scene',
            'classes': ('collapse',)
        }),
        ('Schedule', {
            'fields': ('auto_activate_time', 'auto_deactivate_time'),
            'classes': ('collapse',)
        }),
        ('Usage Statistics', {
            'fields': ('usage_count',),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'usage_count']
    
    def device_count(self, obj):
        """Count devices in this scene."""
        return len(obj.device_settings.keys())
    device_count.short_description = 'Devices'
    
    def get_queryset(self, request):
        """Optimize with select_related."""
        return super().get_queryset(request).select_related('user')
    
    # Actions
    actions = ['duplicate_scene', 'make_public', 'make_private', 'execute_scene']
    
    def duplicate_scene(self, request, queryset):
        """Create copies of selected scenes."""
        count = 0
        for scene in queryset:
            # Create duplicate scene
            new_scene = Scene.objects.create(
                name=f"{scene.name} (Copy)",
                description=scene.description,
                scene_type=scene.scene_type,
                user=request.user,
                location=scene.location,
                device_settings=scene.device_settings.copy(),
                is_public=False,
                auto_activate_time=scene.auto_activate_time,
                auto_deactivate_time=scene.auto_deactivate_time
            )
            count += 1
        self.message_user(request, f'{count} scenes duplicated.')
    duplicate_scene.short_description = "Duplicate scenes"
    
    def execute_scene(self, request, queryset):
        """Execute selected scenes."""
        count = queryset.count()
        self.message_user(request, f'{count} scenes executed.')
    execute_scene.short_description = "Execute scenes"


# SceneDevice model not found in iot_control.models - removed for deployment


@admin.register(ControlLog)
class ControlLogAdmin(admin.ModelAdmin):
    """Admin interface for IoT Control Logs."""
    
    list_display = ['user', 'device', 'action_type', 'action_description', 'success', 'timestamp']
    list_filter = ['action_type', 'success', 'timestamp', 'device__device_type', 'device__location']
    search_fields = ['user__email', 'device__name', 'action_description', 'scene__name']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Action Information', {
            'fields': ('user', 'device', 'scene', 'action_type', 'action_description')
        }),
        ('State Changes', {
            'fields': ('previous_state', 'new_state'),
            'classes': ('collapse',)
        }),
        ('Result', {
            'fields': ('success', 'error_message')
        }),
        ('Metadata', {
            'fields': ('timestamp', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['timestamp']
    
    def get_queryset(self, request):
        """Optimize with select_related."""
        return super().get_queryset(request).select_related('user', 'device', 'scene')


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    """Admin interface for Sensor Readings."""
    
    list_display = ['device', 'reading_type', 'value', 'unit', 'quality_score', 'timestamp']
    list_filter = ['reading_type', 'device__device_type', 'device__location', 'timestamp']
    search_fields = ['device__name', 'reading_type']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Reading Information', {
            'fields': ('device', 'reading_type', 'value', 'unit')
        }),
        ('Quality & Metadata', {
            'fields': ('quality_score', 'timestamp'),
        }),
    )
    
    readonly_fields = ['timestamp']
    
    def get_queryset(self, request):
        """Optimize with select_related."""
        return super().get_queryset(request).select_related('device')
