from rest_framework.permissions import BasePermission, SAFE_METHODS, DjangoModelPermissions

class ReadOnlyOrDjangoModelPermissions(BasePermission):


    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        django_perm = DjangoModelPermissions()
        return django_perm.has_permission(request, view)