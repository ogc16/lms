from rest_framework.permissions import BasePermission
from .models import User


class IsInstructorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in (User.Role.INSTRUCTOR, User.Role.ADMIN)
