from common.permissions import ReadOnlyOrContentManager

# Public read, writes restricted to ADMIN/SUPER_ADMIN/EDITOR roles.
DestinationPermission = ReadOnlyOrContentManager
