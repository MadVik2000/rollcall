"""
This file contains all the custom permission classes related to users module
"""

from rest_framework.permissions import IsAuthenticated

from users.models import UserRole


class IsManager(IsAuthenticated):
    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            and request.user
            and request.user.userrole_set.filter(
                role=UserRole.Role.MANAGER, date_deleted__isnull=True
            ).exists()
        )


class IsStaffMember(IsAuthenticated):
    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            and request.user
            and request.user.userrole_set.filter(
                role=UserRole.Role.STAFF_MEMBER, date_deleted__isnull=True
            ).exists()
        )
