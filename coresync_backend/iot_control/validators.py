"""
IoT Control Validators.
Валідація даних для IoT команд та налаштувань.
"""
import re
from typing import Dict, Any
from django.core.exceptions import ValidationError


def validate_hex_color(value: str) -> str:
    """
    Валідувати hex color код.
    Приймає формати: #RGB, #RRGGBB, #RRGGBBAA
    """
    if not value:
        return value
    
    if not value.startswith('#'):
        raise ValidationError('Color must start with #')
    
    hex_pattern = re.compile(r'^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$')
    if not hex_pattern.match(value):
        raise ValidationError('Invalid hex color format. Use #RRGGBB')
    
    return value.upper()


def validate_brightness(value: int) -> int:
    """Валідувати brightness (0-100)"""
    if not isinstance(value, int):
        raise ValidationError('Brightness must be an integer')
    
    if not 0 <= value <= 100:
        raise ValidationError('Brightness must be between 0 and 100')
    
    return value


def validate_temperature(value: float, unit: str = 'fahrenheit') -> float:
    """Валідувати температуру"""
    if not isinstance(value, (int, float)):
        raise ValidationError('Temperature must be a number')
    
    if unit == 'fahrenheit':
        if not 60.0 <= value <= 85.0:
            raise ValidationError('Temperature must be between 60°F and 85°F')
    elif unit == 'celsius':
        if not 15.0 <= value <= 30.0:
            raise ValidationError('Temperature must be between 15°C and 30°C')
    
    return float(value)


def validate_device_id(device_id: str) -> str:
    """Валідувати device ID"""
    if not device_id:
        raise ValidationError('Device ID is required')
    
    if len(device_id) > 100:
        raise ValidationError('Device ID too long (max 100 chars)')
    
    # Дозволені символи: літери, цифри, дефіс, підкреслення
    if not re.match(r'^[a-zA-Z0-9_-]+$', device_id):
        raise ValidationError('Device ID can only contain letters, numbers, _ and -')
    
    return device_id


def validate_ip_address(ip: str) -> str:
    """Валідувати IP адресу"""
    if not ip:
        return ip
    
    ip_pattern = re.compile(
        r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    )
    
    if not ip_pattern.match(ip):
        raise ValidationError('Invalid IP address format')
    
    return ip


def validate_mac_address(mac: str) -> str:
    """Валідувати MAC адресу"""
    if not mac:
        return mac
    
    # Формати: AA:BB:CC:DD:EE:FF або AA-BB-CC-DD-EE-FF
    mac_pattern = re.compile(
        r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    )
    
    if not mac_pattern.match(mac):
        raise ValidationError('Invalid MAC address format. Use AA:BB:CC:DD:EE:FF')
    
    return mac.upper()


def validate_scene_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Валідувати налаштування сцени.
    Перевіряє структуру та значення device settings.
    """
    if not isinstance(settings, dict):
        raise ValidationError('Scene settings must be a dictionary')
    
    if not settings:
        raise ValidationError('Scene settings cannot be empty')
    
    if len(settings) > 50:
        raise ValidationError('Too many devices in scene (max 50)')
    
    # Валідувати кожен device setting
    for device_id, device_settings in settings.items():
        validate_device_id(device_id)
        
        if not isinstance(device_settings, dict):
            raise ValidationError(f'Settings for device {device_id} must be a dictionary')
        
        # Валідувати окремі параметри якщо присутні
        if 'brightness' in device_settings:
            validate_brightness(device_settings['brightness'])
        
        if 'color' in device_settings:
            validate_hex_color(device_settings['color'])
        
        if 'temperature' in device_settings:
            validate_temperature(device_settings['temperature'])
    
    return settings


def validate_command_payload(action: str, payload: Dict[str, Any]) -> bool:
    """
    Валідувати payload команди управління.
    Різні дії вимагають різних payload структур.
    """
    if action == 'set_value':
        if not payload:
            raise ValidationError('set_value requires payload with values')
    
    elif action == 'adjust':
        if not payload:
            raise ValidationError('adjust requires payload with adjustment values')
    
    elif action in ['turn_on', 'turn_off']:
        # Ці команди не потребують payload
        pass
    
    else:
        raise ValidationError(f'Unknown action: {action}')
    
    return True


def validate_location_access(user, location: str) -> bool:
    """
    Валідувати чи користувач має доступ до локації.
    Базується на membership tier.
    """
    if not user or not user.is_authenticated:
        raise ValidationError('User must be authenticated')
    
    membership_status = user.membership_status
    
    # VIP має доступ скрізь
    if membership_status == 'vip':
        return True
    
    # Basic/Premium - тільки Mensuite
    if membership_status in ['basic', 'premium']:
        if location.startswith('mensuite_') or location.startswith('common_'):
            return True
    
    # Premium - також Coresync Private
    if membership_status == 'premium':
        if location.startswith('coresync_'):
            return True
    
    raise ValidationError(f'No access to location: {location}')


def validate_scene_name(name: str) -> str:
    """Валідувати назву сцени"""
    if not name:
        raise ValidationError('Scene name is required')
    
    if len(name) < 3:
        raise ValidationError('Scene name too short (min 3 chars)')
    
    if len(name) > 100:
        raise ValidationError('Scene name too long (max 100 chars)')
    
    # Заборонені символи
    if any(char in name for char in ['<', '>', '"', "'"]):
        raise ValidationError('Scene name contains forbidden characters')
    
    return name.strip()


def validate_volume(value: int) -> int:
    """Валідувати гучність (0-100)"""
    if not isinstance(value, int):
        raise ValidationError('Volume must be an integer')
    
    if not 0 <= value <= 100:
        raise ValidationError('Volume must be between 0 and 100')
    
    return value


def validate_intensity(value: int, min_val: int = 0, max_val: int = 5) -> int:
    """Валідувати intensity (для ароматів тощо)"""
    if not isinstance(value, int):
        raise ValidationError('Intensity must be an integer')
    
    if not min_val <= value <= max_val:
        raise ValidationError(f'Intensity must be between {min_val} and {max_val}')
    
    return value

