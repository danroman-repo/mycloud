from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Доступ к файлу только владельцу или администратору.
    """
    
    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        
        if request.user.is_admin:
            return True
        
        return False


class IsAdminOrSelf(permissions.BasePermission):
    """
    Доступ к списку файлов: админ может видеть файлы любого пользователя,
    обычный пользователь — только свои.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_admin:
            return True
        
        return True