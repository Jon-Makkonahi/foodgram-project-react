from rest_framework import permissions


class IsAdminOrReadOnly(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_staff or obj.pk == user.pk
