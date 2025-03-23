from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # For playlists, check if the requesting user is the owner
        if hasattr(obj, 'user'):
            return str(obj.user) == str(request.user.username)

        # Write permissions are only allowed to the owner
        return obj.id == request.user.id
