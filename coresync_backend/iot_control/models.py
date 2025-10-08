"""
IoT Control models for the CoreSync application.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseModel


class IoTDevice(BaseModel):
    """
    Physical IoT devices in the spa that can be controlled.
    """
    DEVICE_TYPES = [
        ('lighting', 'Lighting System'),
        ('scent', 'Scent Diffuser'),
        ('temperature', 'Temperature Control'),
        ('music', 'Music System'),
        ('massage', 'Massage Equipment'),
        ('sauna', 'Sauna Control'),
        ('jacuzzi', 'Jacuzzi Control'),
        ('mirror', 'Smart Mirror'),
        ('security', 'Security System'),
    ]

    LOCATION_CHOICES = [
        ('mensuite_main', 'Mensuite - Main Area'),
        ('mensuite_meditation', 'Mensuite - Meditation Room'),
        ('mensuite_barber', 'Mensuite - Barber Area'),
        ('mensuite_laser', 'Mensuite - Laser Treatment'),
        ('coresync_suite', 'Coresync Private - Main Suite'),
        ('coresync_sauna', 'Coresync Private - Sauna'),
        ('coresync_jacuzzi', 'Coresync Private - Jacuzzi'),
        ('coresync_outdoor', 'Coresync Private - Outdoor Area'),
        ('common_lobby', 'Common - Lobby'),
        ('common_reception', 'Common - Reception'),
    ]

    name = models.CharField(max_length=100)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES)
    location = models.CharField(max_length=30, choices=LOCATION_CHOICES)
    
    # Device identification
    device_id = models.CharField(max_length=100, unique=True)
    manufacturer = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    firmware_version = models.CharField(max_length=50, blank=True)
    
    # Network configuration
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    mac_address = models.CharField(max_length=17, blank=True)
    
    # Status and configuration
    current_status = models.JSONField(default=dict, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_online = models.BooleanField(default=False)
    
    # Control settings
    min_value = models.FloatField(default=0)
    max_value = models.FloatField(default=100)
    default_value = models.FloatField(default=50)
    
    # Security
    api_key = models.CharField(max_length=255, blank=True)
    requires_authentication = models.BooleanField(default=True)

    class Meta:
        db_table = 'iot_devices'
        verbose_name = 'IoT Device'
        verbose_name_plural = 'IoT Devices'
        ordering = ['location', 'device_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_location_display()})"

    def update_status(self, status_data):
        """Update device status and save."""
        self.current_status.update(status_data)
        self.is_online = True
        self.save()


class Scene(BaseModel):
    """
    Predefined or custom scenes that control multiple IoT devices.
    """
    SCENE_TYPES = [
        ('preset', 'Preset Scene'),
        ('custom', 'Custom User Scene'),
        ('automatic', 'Automatic Scene'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    scene_type = models.CharField(max_length=20, choices=SCENE_TYPES)
    
    # Ownership
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='scenes',
        null=True,
        blank=True,
        help_text="Leave blank for preset scenes"
    )
    
    # Location restriction
    location = models.CharField(
        max_length=30,
        choices=IoTDevice.LOCATION_CHOICES,
        blank=True,
        help_text="Restrict scene to specific location"
    )
    
    # Scene configuration
    device_settings = models.JSONField(
        default=dict,
        help_text="Settings for each device in the scene"
    )
    
    # Metadata
    is_public = models.BooleanField(
        default=False,
        help_text="Allow other users to see and use this scene"
    )
    usage_count = models.PositiveIntegerField(default=0)
    
    # Schedule
    auto_activate_time = models.TimeField(blank=True, null=True)
    auto_deactivate_time = models.TimeField(blank=True, null=True)

    class Meta:
        db_table = 'scenes'
        verbose_name = 'Scene'
        verbose_name_plural = 'Scenes'
        ordering = ['scene_type', 'name']

    def __str__(self):
        owner = f" ({self.user.full_name})" if self.user else ""
        return f"{self.name}{owner}"

    def activate(self):
        """Activate this scene by applying all device settings."""
        for device_id, settings in self.device_settings.items():
            try:
                device = IoTDevice.objects.get(device_id=device_id)
                device.update_status(settings)
            except IoTDevice.DoesNotExist:
                continue
        
        self.usage_count += 1
        self.save()


class ControlLog(models.Model):
    """
    Log of all IoT control actions for security and debugging.
    """
    ACTION_TYPES = [
        ('manual', 'Manual Control'),
        ('scene', 'Scene Activation'),
        ('automatic', 'Automatic Control'),
        ('emergency', 'Emergency Action'),
    ]

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='control_logs',
        null=True,
        blank=True
    )
    device = models.ForeignKey(
        IoTDevice,
        on_delete=models.CASCADE,
        related_name='control_logs',
        null=True,
        blank=True
    )
    scene = models.ForeignKey(
        Scene,
        on_delete=models.SET_NULL,
        related_name='control_logs',
        null=True,
        blank=True
    )
    
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    action_description = models.CharField(max_length=255)
    
    # Control details
    previous_state = models.JSONField(default=dict, blank=True)
    new_state = models.JSONField(default=dict, blank=True)
    
    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    # Status
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = 'control_logs'
        verbose_name = 'Control Log'
        verbose_name_plural = 'Control Logs'
        ordering = ['-timestamp']

    def __str__(self):
        user_info = f"{self.user.full_name} - " if self.user else "System - "
        return f"{user_info}{self.action_description} at {self.timestamp}"


class SensorReading(models.Model):
    """
    Sensor readings from IoT devices for monitoring and analytics.
    """
    device = models.ForeignKey(
        IoTDevice,
        on_delete=models.CASCADE,
        related_name='sensor_readings',
        null=True,
        blank=True
    )
    
    # Reading data
    reading_type = models.CharField(
        max_length=50,
        help_text="Type of sensor reading (temperature, humidity, etc.)"
    )
    value = models.FloatField()
    unit = models.CharField(max_length=20, blank=True)
    
    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    quality_score = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Reading quality from 0.0 to 1.0"
    )

    class Meta:
        db_table = 'sensor_readings'
        verbose_name = 'Sensor Reading'
        verbose_name_plural = 'Sensor Readings'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', 'reading_type', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.device.name} - {self.reading_type}: {self.value} {self.unit}"
