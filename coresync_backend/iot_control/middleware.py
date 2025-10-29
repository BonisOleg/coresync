"""
IoT Control Middleware.
Rate limiting та security middleware для IoT операцій.
"""
import logging
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings

logger = logging.getLogger(__name__)


class IoTRateLimitMiddleware:
    """
    Middleware для rate limiting IoT команд.
    Обмежує кількість команд на хвилину для запобігання зловживань.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = getattr(settings, 'IOT_COMMAND_RATE_LIMIT', 100)
        self.window = 60  # 60 секунд
    
    def __call__(self, request):
        # Перевірити чи це IoT endpoint
        if request.path.startswith('/api/iot/') and request.method in ['POST', 'PUT', 'PATCH']:
            
            # Отримати user ID
            if not request.user or not request.user.is_authenticated:
                # Анонімні користувачі не можуть керувати IoT
                return JsonResponse({
                    'error': 'Authentication required for IoT control'
                }, status=401)
            
            user_id = request.user.id
            cache_key = f'iot_rate_limit:{user_id}'
            
            # Перевірити поточний count
            current_count = cache.get(cache_key, 0)
            
            if current_count >= self.rate_limit:
                logger.warning(
                    f"IoT rate limit exceeded for user {user_id}: "
                    f"{current_count}/{self.rate_limit}"
                )
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'detail': f'Maximum {self.rate_limit} IoT commands per minute',
                    'retry_after': self.window
                }, status=429)
            
            # Increment counter
            cache.set(cache_key, current_count + 1, self.window)
        
        response = self.get_response(request)
        return response


class IoTSecurityMiddleware:
    """
    Middleware для додаткової безпеки IoT операцій.
    Логування всіх IoT команд та перевірка прав доступу.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Логувати IoT команди
        if request.path.startswith('/api/iot/') and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            
            user = request.user if request.user.is_authenticated else None
            ip_address = self._get_client_ip(request)
            
            logger.info(
                f"IoT Command: {request.method} {request.path} | "
                f"User: {user.username if user else 'Anonymous'} | "
                f"IP: {ip_address}"
            )
            
            # Перевірити IoT enabled
            if not getattr(settings, 'IOT_CONTROL_ENABLED', True):
                return JsonResponse({
                    'error': 'IoT control is temporarily disabled'
                }, status=503)
        
        response = self.get_response(request)
        return response
    
    @staticmethod
    def _get_client_ip(request):
        """Отримати IP адресу клієнта"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip

