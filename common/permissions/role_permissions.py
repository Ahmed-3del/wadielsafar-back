from rest_framework.permissions import SAFE_METHODS, BasePermission

from common.constants import STAFF_CONTENT_ROLES, STAFF_SALES_ROLES, RoleChoices


class HasRole(BasePermission):
    """Base class for role-gated permissions. Subclass and set `allowed_roles`
    rather than instantiating directly."""

    allowed_roles = ()

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or user.role in self.allowed_roles)
        )


class IsSuperAdmin(HasRole):
    allowed_roles = (RoleChoices.SUPER_ADMIN,)


class IsContentManager(HasRole):
    """Roles allowed to manage catalog content: destinations, packages, visas, etc."""

    allowed_roles = STAFF_CONTENT_ROLES


class IsSalesStaff(HasRole):
    """Roles allowed to view/manage leads and inquiries."""

    allowed_roles = STAFF_SALES_ROLES


class IsStaffUser(BasePermission):
    """Any authenticated staff account (all roles), used for read-only
    staff-facing resources such as the users directory."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.is_staff or user.role))


class ReadOnlyOrContentManager(BasePermission):
    """Public GET/HEAD/OPTIONS; writes restricted to content-managing roles.
    Used by public catalog viewsets (destinations, packages, visas, ...)."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return IsContentManager().has_permission(request, view)
