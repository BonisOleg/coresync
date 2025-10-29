"""
IoT Control Serializers для CoreSync API.
DRF serializers для пристроїв, сцен та управління.
"""
from rest_framework import serializers
from .models import IoTDevice, Scene, ControlLog, SensorReading
from .validators import (
    validate_hex_color,
    validate_brightness,
    validate_temperature,
    validate_scene_settings,
    validate_scene_name
)
from django.contrib.auth import get_user_model

User = get_user_model()


class IoTDeviceSerializer(serializers.ModelSerializer):
    """Serializer для IoT пристроїв"""
    
    location_display = serializers.CharField(source='get_location_display', read_only=True)
    device_type_display = serializers.CharField(source='get_device_type_display', read_only=True)
    connection_status = serializers.SerializerMethodField()
    
    class Meta:
        model = IoTDevice
        fields = [
            'id', 'name', 'device_type', 'device_type_display',
            'location', 'location_display', 'device_id',
            'manufacturer', 'model', 'firmware_version',
            'current_status', 'is_online', 'connection_status',
            'last_updated', 'min_value', 'max_value', 'default_value',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'last_updated', 'created_at', 'is_online']
    
    def get_connection_status(self, obj):
        """Отримати статус підключення"""
        return 'online' if obj.is_online else 'offline'


class IoTDeviceListSerializer(serializers.ModelSerializer):
    """Скорочений serializer для списку пристроїв"""
    
    location_display = serializers.CharField(source='get_location_display', read_only=True)
    device_type_display = serializers.CharField(source='get_device_type_display', read_only=True)
    
    class Meta:
        model = IoTDevice
        fields = [
            'id', 'name', 'device_type', 'device_type_display',
            'location', 'location_display', 'is_online', 'current_status'
        ]


class DeviceControlSerializer(serializers.Serializer):
    """Serializer для команд управління пристроями"""
    
    device_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=[
        ('set_value', 'Set Value'),
        ('turn_on', 'Turn On'),
        ('turn_off', 'Turn Off'),
        ('adjust', 'Adjust'),
    ])
    value = serializers.JSONField(required=False)
    
    def validate_device_id(self, value):
        """Перевірити існування пристрою"""
        if not IoTDevice.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Device not found or inactive")
        return value
    
    def validate(self, data):
        """Валідація команди"""
        action = data.get('action')
        
        # Для set_value та adjust обов'язкове поле value
        if action in ['set_value', 'adjust'] and 'value' not in data:
            raise serializers.ValidationError({
                'value': 'This field is required for the selected action'
            })
        
        return data


class SceneSerializer(serializers.ModelSerializer):
    """Serializer для сцен"""
    
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    scene_type_display = serializers.CharField(source='get_scene_type_display', read_only=True)
    location_display = serializers.CharField(source='get_location_display', read_only=True)
    device_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Scene
        fields = [
            'id', 'name', 'description', 'scene_type', 'scene_type_display',
            'user', 'user_name', 'location', 'location_display',
            'device_settings', 'is_public', 'usage_count',
            'auto_activate_time', 'auto_deactivate_time',
            'is_active', 'created_at', 'device_count'
        ]
        read_only_fields = ['id', 'usage_count', 'created_at', 'user_name']
    
    def get_device_count(self, obj):
        """Кількість пристроїв у сцені"""
        return len(obj.device_settings.keys()) if obj.device_settings else 0
    
    def validate_name(self, value):
        """Валідація назви сцени"""
        return validate_scene_name(value)
    
    def validate_device_settings(self, value):
        """Валідація налаштувань пристроїв"""
        return validate_scene_settings(value)


class SceneListSerializer(serializers.ModelSerializer):
    """Скорочений serializer для списку сцен"""
    
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    device_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Scene
        fields = [
            'id', 'name', 'scene_type', 'user_name',
            'is_public', 'usage_count', 'device_count'
        ]
    
    def get_device_count(self, obj):
        return len(obj.device_settings.keys()) if obj.device_settings else 0


class SceneActivationSerializer(serializers.Serializer):
    """Serializer для активації сцени"""
    
    scene_id = serializers.IntegerField()
    
    def validate_scene_id(self, value):
        """Перевірити існування сцени"""
        try:
            scene = Scene.objects.get(id=value, is_active=True)
            
            # Перевірити доступ
            request = self.context.get('request')
            if request and request.user:
                # Дозволити власні та публічні сцени
                if not scene.is_public and scene.user != request.user:
                    raise serializers.ValidationError("You don't have access to this scene")
            
            return value
        except Scene.DoesNotExist:
            raise serializers.ValidationError("Scene not found or inactive")


class ControlLogSerializer(serializers.ModelSerializer):
    """Serializer для логів управління"""
    
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    device_name = serializers.CharField(source='device.name', read_only=True)
    scene_name = serializers.CharField(source='scene.name', read_only=True)
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    
    class Meta:
        model = ControlLog
        fields = [
            'id', 'user', 'user_name', 'device', 'device_name',
            'scene', 'scene_name', 'action_type', 'action_type_display',
            'action_description', 'previous_state', 'new_state',
            'success', 'error_message', 'timestamp', 'ip_address'
        ]
        read_only_fields = ['id', 'timestamp']


class SensorReadingSerializer(serializers.ModelSerializer):
    """Serializer для показань сенсорів"""
    
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = SensorReading
        fields = [
            'id', 'device', 'device_name', 'reading_type',
            'value', 'unit', 'quality_score', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class LightingControlSerializer(serializers.Serializer):
    """Serializer для управління освітленням"""
    
    location = serializers.ChoiceField(choices=IoTDevice.LOCATION_CHOICES)
    brightness = serializers.IntegerField(min_value=0, max_value=100)
    color = serializers.CharField(max_length=7, required=False, allow_blank=True)
    
    def validate_color(self, value):
        """Валідація hex кольору"""
        if value:
            return validate_hex_color(value)
        return value


class TemperatureControlSerializer(serializers.Serializer):
    """Serializer для управління температурою"""
    
    location = serializers.ChoiceField(choices=IoTDevice.LOCATION_CHOICES)
    temperature = serializers.FloatField(min_value=60.0, max_value=85.0)
    
    def validate_temperature(self, value):
        """Валідація температури (Fahrenheit)"""
        return validate_temperature(value, unit='fahrenheit')


class ScentControlSerializer(serializers.Serializer):
    """Serializer для управління ароматом"""
    
    location = serializers.ChoiceField(choices=IoTDevice.LOCATION_CHOICES)
    scent_type = serializers.ChoiceField(choices=[
        ('lavender', 'Lavender'),
        ('eucalyptus', 'Eucalyptus'),
        ('citrus', 'Citrus'),
        ('vanilla', 'Vanilla'),
        ('mint', 'Mint'),
        ('ocean', 'Ocean Breeze'),
        ('forest', 'Forest'),
        ('off', 'Off')
    ])
    intensity = serializers.IntegerField(min_value=0, max_value=5, default=3)


class MusicControlSerializer(serializers.Serializer):
    """Serializer для управління музикою"""
    
    location = serializers.ChoiceField(choices=IoTDevice.LOCATION_CHOICES)
    action = serializers.ChoiceField(choices=[
        ('play', 'Play'),
        ('pause', 'Pause'),
        ('stop', 'Stop'),
        ('next', 'Next Track'),
        ('previous', 'Previous Track')
    ])
    volume = serializers.IntegerField(min_value=0, max_value=100, required=False)
    playlist = serializers.CharField(max_length=200, required=False, allow_blank=True)

