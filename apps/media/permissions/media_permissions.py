from common.permissions import IsStaffUser

# Internal content library used by admins to attach assets elsewhere — not a
# public gallery, so both upload and list require staff auth.
MediaPermission = IsStaffUser
