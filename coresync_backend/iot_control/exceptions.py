"""
IoT Control Custom Exceptions.
Спеціалізовані exceptions для IoT операцій.
"""
from rest_framework.exceptions import APIException
from rest_framework import status


class IoTDeviceOfflineException(APIException):
    """Пристрій offline та недоступний"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'IoT device is currently offline'
    default_code = 'device_offline'


class IoTDeviceNotFoundException(APIException):
    """Пристрій не знайдено"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'IoT device not found'
    default_code = 'device_not_found'


class IoTCommandFailedException(APIException):
    """Команда не виконалася"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'IoT command execution failed'
    default_code = 'command_failed'


class IoTAccessDeniedException(APIException):
    """Немає доступу до пристрою/локації"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Access to this IoT device or location is denied'
    default_code = 'access_denied'


class IoTRateLimitException(APIException):
    """Перевищено rate limit"""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Too many IoT commands. Please slow down'
    default_code = 'rate_limit_exceeded'


class IoTInvalidCommandException(APIException):
    """Невалідна команда"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid IoT command or parameters'
    default_code = 'invalid_command'


class IoTSceneNotFoundException(APIException):
    """Сцену не знайдено"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'IoT scene not found'
    default_code = 'scene_not_found'


class IoTSceneActivationException(APIException):
    """Помилка активації сцени"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Failed to activate IoT scene'
    default_code = 'scene_activation_failed'


class IoTWebSocketException(Exception):
    """WebSocket connection exception"""
    pass

