from django.core.cache import cache

from rest_framework.permissions import BasePermission

from tournaments.models import UserProfile


class OTPRequired(BasePermission):

    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated
            and cache.get(
                f"otp_good_{request.user.pk}",
                False
            )
        )


class IsAdmin(BasePermission):

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            return False

        return profile.role == UserProfile.Role.ADMIN