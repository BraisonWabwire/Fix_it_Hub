from rest_framework.permissions import BasePermission

class RoleBasedPermission(BasePermission):
    allowed_roles = []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in self.allowed_roles

class IsAdmin(RoleBasedPermission):
    allowed_roles = ['admin']

class IsHandyman(RoleBasedPermission):
    allowed_roles = ['handyman']

class IsClient(RoleBasedPermission):
    allowed_roles = ['client']

class IsOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'admin'

    def has_object_permission(self, request, view, obj):
        return request.user.role == 'admin' or obj == request.user