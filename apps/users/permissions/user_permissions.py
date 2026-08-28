from common.permissions import IsStaffUser

# Re-exported under an app-local name so viewsets import from
# apps.users.permissions rather than reaching into common directly.
IsStaffDirectoryReader = IsStaffUser
