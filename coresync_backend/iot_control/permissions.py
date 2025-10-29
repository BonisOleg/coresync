"""
IoT Control Permissions для CoreSync.
Доступ до управління IoT пристроями тільки для авторизованих членів.
"""
from rest_framework import permissions


class IsMemberUser(permissions.BasePermission):
    """
    Дозвіл тільки для членів спа.
    Non-members не можуть керувати IoT пристроями.
    """
    
    message = "Only spa members can control IoT devices"
    
    def has_permission(self, request, view):
        """Перевірити чи користувач є членом"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Перевірити membership status
        return request.user.is_member


class IsDeviceOwnerOrPublic(permissions.BasePermission):
    """
    Дозвіл на перегляд/редагування сцен:
    - Власні сцени
    - Публічні сцени (тільки читання)
    """
    
    def has_object_permission(self, request, view, obj):
        """Перевірити доступ до конкретної сцени"""
        # GET, HEAD, OPTIONS - дозволено для публічних
        if request.method in permissions.SAFE_METHODS:
            return obj.is_public or obj.user == request.user
        
        # POST, PUT, PATCH, DELETE - тільки для власника
        return obj.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Адміністратор може все, інші тільки читання.
    """
    
    def has_permission(self, request, view):
        """Перевірити чи користувач адмін"""
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user and request.user.is_staff


class CanControlLocation(permissions.BasePermission):
    """
    Перевірити доступ до конкретної локації на основі membership.
    """
    
    message = "Your membership doesn't grant access to this location"
    
    def has_permission(self, request, view):
        """Перевірити доступ до локації"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        location = request.data.get('location', '')
        membership_status = request.user.membership_status
        
        # Unlimited members - повний доступ
        if membership_status == 'vip':
            return True
        
        # Mensuite members
        if membership_status in ['basic', 'premium']:
            if location.startswith('mensuite_'):
                return True
        
        # Private members
        if membership_status == 'premium':
            if location.startswith('coresync_'):
                return True
        
        # Common areas доступні всім членам
        if location.startswith('common_'):
            return True
        
        return False

