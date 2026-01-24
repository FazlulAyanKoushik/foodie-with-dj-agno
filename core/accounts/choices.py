from django.db.models import TextChoices


class UserRole(TextChoices):
    USER = 'user', 'User'
    RESTAURANT_OWNER = 'restaurant_owner', 'Restaurant Owner'
    PLATFORM_ADMIN = 'platform_admin', 'Platform Admin'
    SUPER_ADMIN = 'super_admin', 'Super Admin'

