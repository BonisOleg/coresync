"""
Django Admin configuration for IoT Control app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from django.utils import timezone
from .models import IoTDevice, Scene, SceneDevice, UserPreference


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
    
    list_display = ['name', 'category', 'creator', 'device_count', 'is_public', 'usage_count', 'is_active']
    list_filter = ['category', 'is_public', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'creator__username']
    ordering = ['category', 'name']
    
    fieldsets = (
        ('Scene Information', {
            'fields': ('name', 'description', 'category', 'icon')
        }),
        ('Access Control', {
            'fields': ('creator', 'is_public', 'allowed_users'),
            'description': 'Who can view and use this scene'
        }),
        ('Execution Settings', {
            'fields': ('execution_delay', 'transition_duration'),
            'classes': ('collapse',)
        }),
        ('Usage Statistics', {
            'fields': ('usage_count', 'last_used_at'),
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
    
    readonly_fields = ['created_at', 'updated_at', 'usage_count', 'last_used_at']
    filter_horizontal = ['allowed_users']
    
    def device_count(self, obj):
        """Count devices in this scene."""
        return obj.devices.count()
    device_count.short_description = 'Devices'
    
    def get_queryset(self, request):
        """Optimize with select_related and annotations."""
        return super().get_queryset(request).select_related('creator').annotate(
            device_count=Count('scene_devices')
        )
    
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
                category=scene.category,
                creator=request.user,
                is_public=False,
                execution_delay=scene.execution_delay,
                transition_duration=scene.transition_duration
            )
            # Copy scene devices
            for scene_device in scene.scene_devices.all():
                SceneDevice.objects.create(
                    scene=new_scene,
                    device=scene_device.device,
                    target_value=scene_device.target_value,
                    target_color=scene_device.target_color,
                    target_temperature=scene_device.target_temperature,
                    delay=scene_device.delay
                )
            count += 1
        self.message_user(request, f'{count} scenes duplicated.')
    duplicate_scene.short_description = "Duplicate scenes"
    
    def execute_scene(self, request, queryset):
        """Execute selected scenes."""
        count = queryset.count()
        self.message_user(request, f'{count} scenes executed.')
    execute_scene.short_description = "Execute scenes"


@admin.register(SceneDevice)
class SceneDeviceAdmin(admin.ModelAdmin):
    """Admin interface for Scene Device Settings."""
    
    list_display = ['scene', 'device', 'target_value', 'target_color', 'delay', 'is_enabled']
    list_filter = ['scene', 'device__device_type', 'device__location', 'is_enabled']
    search_fields = ['scene__name', 'device__name']
    ordering = ['scene', 'device']
    
    fieldsets = (
        ('Assignment', {
            'fields': ('scene', 'device')
        }),
        ('Target Settings', {
            'fields': ('target_value', 'target_color', 'target_temperature'),
            'description': 'Device settings when this scene is activated'
        }),
        ('Timing', {
            'fields': ('delay',),
            'description': 'Delay before applying settings (in seconds)'
        }),
        ('Status', {
            'fields': ('is_enabled',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    """Admin interface for User IoT Preferences."""
    
    list_display = ['user', 'preferred_lighting', 'preferred_temperature', 'preferred_scent', 'auto_scenes_enabled']
    list_filter = ['auto_scenes_enabled', 'preferred_scent', 'created_at']
    search_fields = ['user__username', 'user__email']
    ordering = ['user']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Lighting Preferences', {
            'fields': ('preferred_lighting', 'preferred_color'),
            'classes': ('collapse',)
        }),
        ('Environmental Preferences', {
            'fields': ('preferred_temperature', 'preferred_scent', 'preferred_music_genre'),
            'classes': ('collapse',)
        }),
        ('Scene Preferences', {
            'fields': ('favorite_scenes', 'auto_scenes_enabled'),
            'description': 'Automatic scene activation and favorites'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['favorite_scenes']
    
    def get_queryset(self, request):
        """Optimize with select_related."""
        return super().get_queryset(request).select_related('user')
    
    # Actions
    actions = ['enable_auto_scenes', 'disable_auto_scenes', 'reset_preferences']
    
    def enable_auto_scenes(self, request, queryset):
        """Enable automatic scenes for selected users."""
        updated = queryset.update(auto_scenes_enabled=True)
        self.message_user(request, f'Auto scenes enabled for {updated} users.')
    enable_auto_scenes.short_description = "Enable auto scenes"
    
    def disable_auto_scenes(self, request, queryset):
        """Disable automatic scenes for selected users."""
        updated = queryset.update(auto_scenes_enabled=False)
        self.message_user(request, f'Auto scenes disabled for {updated} users.')
    disable_auto_scenes.short_description = "Disable auto scenes"


# Inline admin for scene devices
class SceneDeviceInline(admin.TabularInline):
    """Inline admin for scene device configurations."""
    model = SceneDevice
    extra = 1
    fields = ['device', 'target_value', 'target_color', 'target_temperature', 'delay', 'is_enabled']


# Add inline to SceneAdmin
SceneAdmin.inlines = [SceneDeviceInline]
