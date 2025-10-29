"""
Technicians Permissions - Custom permission classes.
"""
from rest_framework.permissions import BasePermission


class IsTechnicianOrManager(BasePermission):
    """
    Permission: User є technician або manager.
    Technician can read own data, manager can read all.
    """
    
    def has_permission(self, request, view):
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Manager (staff) has full access
        if request.user.is_staff:
            return True
        
        # Check if user has technician profile
        try:
            technician = request.user.technician_profile
            return technician.is_active
        except:
            return False
    
    def has_object_permission(self, request, view, obj):
        # Manager has full access
        if request.user.is_staff:
            return True
        
        # Technician can only access own data
        try:
            technician = request.user.technician_profile
            
            # Check object ownership
            if hasattr(obj, 'technician'):
                return obj.technician == technician
            elif hasattr(obj, 'user'):
                return obj.user == request.user
            
            return False
        except:
            return False


class IsManager(BasePermission):
    """
    Permission: Only managers (staff users).
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff

