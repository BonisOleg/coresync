"""
IoT Control Utilities.
Helper functions для IoT операцій.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from django.core.cache import cache
from django.utils import timezone
from django.db import models

logger = logging.getLogger(__name__)


def get_client_ip(request) -> str:
    """
    Отримати IP адресу клієнта з request.
    Враховує proxy headers (X-Forwarded-For).
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    
    return ip


def get_user_agent(request) -> str:
    """Отримати User-Agent з request"""
    return request.META.get('HTTP_USER_AGENT', '')[:500]


def rate_limit_check(user_id: int, action: str, limit: int = 100, window: int = 60) -> bool:
    """
    Перевірити rate limit для користувача.
    
    Args:
        user_id: ID користувача
        action: тип дії (control, scene_activate, etc)
        limit: максимум дій
        window: часове вікно в секундах
    
    Returns:
        bool: True якщо дозволено, False якщо перевищено limit
    """
    cache_key = f'rate_limit:{action}:{user_id}'
    
    current_count = cache.get(cache_key, 0)
    
    if current_count >= limit:
        logger.warning(f"Rate limit exceeded for user {user_id}, action: {action}")
        return False
    
    cache.set(cache_key, current_count + 1, window)
    return True


def sanitize_device_status(status: Dict[str, Any]) -> Dict[str, Any]:
    """
    Очистити device status від небезпечних даних.
    Видалити sensitive інформацію.
    """
    if not isinstance(status, dict):
        return {}
    
    # Список дозволених ключів
    allowed_keys = [
        'power', 'brightness', 'color', 'temperature',
        'volume', 'intensity', 'mode', 'last_action',
        'last_update', 'value'
    ]
    
    sanitized = {
        key: value
        for key, value in status.items()
        if key in allowed_keys
    }
    
    return sanitized


def format_device_response(device, include_details: bool = False) -> Dict[str, Any]:
    """
    Форматувати device для API response.
    
    Args:
        device: IoTDevice instance
        include_details: включити детальну інформацію
    """
    response = {
        'id': device.id,
        'name': device.name,
        'device_type': device.device_type,
        'location': device.location,
        'is_online': device.is_online,
        'current_status': sanitize_device_status(device.current_status),
        'last_updated': device.last_updated.isoformat() if device.last_updated else None
    }
    
    if include_details:
        response.update({
            'device_id': device.device_id,
            'manufacturer': device.manufacturer,
            'model': device.model,
            'firmware_version': device.firmware_version,
            'min_value': device.min_value,
            'max_value': device.max_value,
            'default_value': device.default_value
        })
    
    return response


def calculate_scene_duration(scene_settings: Dict) -> int:
    """
    Розрахувати приблизну тривалість виконання сцени.
    
    Returns:
        int: тривалість в секундах
    """
    device_count = len(scene_settings.keys())
    
    # Базова тривалість: 0.5 секунди на пристрій
    base_duration = device_count * 0.5
    
    # Максимум 30 секунд
    return min(int(base_duration), 30)


def check_device_compatibility(device1_type: str, device2_type: str) -> bool:
    """
    Перевірити чи сумісні два типи пристроїв в одній сцені.
    Деякі комбінації можуть конфліктувати.
    """
    # Список несумісних комбінацій
    incompatible_pairs = [
        # Поки що немає несумісних, але може з'явитись
    ]
    
    pair = tuple(sorted([device1_type, device2_type]))
    return pair not in incompatible_pairs


def generate_device_report(location: str, time_range: int = 24) -> Dict[str, Any]:
    """
    Згенерувати звіт про використання пристроїв.
    
    Args:
        location: локація
        time_range: години для аналізу
    
    Returns:
        dict: статистика використання
    """
    from .models import ControlLog, IoTDevice
    
    start_time = timezone.now() - timedelta(hours=time_range)
    
    devices = IoTDevice.objects.filter(location=location, is_active=True)
    logs = ControlLog.objects.filter(
        device__location=location,
        timestamp__gte=start_time
    )
    
    total_commands = logs.count()
    successful_commands = logs.filter(success=True).count()
    failed_commands = logs.filter(success=False).count()
    
    # Найпопулярніші пристрої
    popular_devices = logs.values('device__name').annotate(
        count=models.Count('id')
    ).order_by('-count')[:5]
    
    # Найактивніші користувачі
    active_users = logs.filter(user__isnull=False).values(
        'user__username'
    ).annotate(
        count=models.Count('id')
    ).order_by('-count')[:5]
    
    report = {
        'location': location,
        'time_range_hours': time_range,
        'total_devices': devices.count(),
        'online_devices': devices.filter(is_online=True).count(),
        'total_commands': total_commands,
        'successful_commands': successful_commands,
        'failed_commands': failed_commands,
        'success_rate': round(successful_commands / total_commands * 100, 2) if total_commands > 0 else 0,
        'popular_devices': list(popular_devices),
        'active_users': list(active_users),
        'generated_at': timezone.now().isoformat()
    }
    
    return report


def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """
    Конвертувати температуру між Fahrenheit та Celsius.
    """
    if from_unit == to_unit:
        return value
    
    if from_unit == 'fahrenheit' and to_unit == 'celsius':
        return round((value - 32) * 5/9, 1)
    
    if from_unit == 'celsius' and to_unit == 'fahrenheit':
        return round(value * 9/5 + 32, 1)
    
    raise ValueError(f'Unknown temperature units: {from_unit} -> {to_unit}')


def is_device_available(device_id: int) -> bool:
    """
    Перевірити чи пристрій доступний для управління.
    Враховує is_online та is_active.
    """
    from .models import IoTDevice
    
    try:
        device = IoTDevice.objects.get(id=device_id)
        return device.is_active and device.is_online
    except IoTDevice.DoesNotExist:
        return False


def batch_update_devices(device_ids: list, status_update: Dict) -> Dict[str, Any]:
    """
    Масове оновлення статусу пристроїв.
    
    Args:
        device_ids: список ID пристроїв
        status_update: нові значення статусу
    
    Returns:
        dict: результат операції
    """
    from .models import IoTDevice
    
    updated_count = 0
    failed_count = 0
    
    for device_id in device_ids:
        try:
            device = IoTDevice.objects.get(id=device_id, is_active=True)
            device.current_status.update(status_update)
            device.save()
            updated_count += 1
        except IoTDevice.DoesNotExist:
            failed_count += 1
        except Exception as e:
            logger.error(f"Failed to update device {device_id}: {str(e)}")
            failed_count += 1
    
    return {
        'success': failed_count == 0,
        'updated': updated_count,
        'failed': failed_count,
        'total': len(device_ids)
    }


def validate_schedule_time(time_str: str) -> bool:
    """
    Валідувати time string для schedule (HH:MM формат).
    """
    try:
        datetime.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False

