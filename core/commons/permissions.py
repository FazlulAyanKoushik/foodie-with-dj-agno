from rest_framework.permissions import BasePermission
from accounts.choices import UserRole


class IsSuperAdmin(BasePermission):
    """
    Allows access only to super admin users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == UserRole.SUPER_ADMIN)


class IsPlatformAdmin(BasePermission):
    """
    Allows access only to platform admin users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == UserRole.PLATFORM_ADMIN)


class IsRestaurantOwner(BasePermission):
    """
    Allows access only to restaurant owners.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == UserRole.RESTAURANT_OWNER)
