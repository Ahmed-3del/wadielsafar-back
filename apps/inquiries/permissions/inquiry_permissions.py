from common.permissions import IsSalesStaff, ReadOnlyOrContentManager

InquiryAdminPermission = IsSalesStaff
# The contact form renders these questions, so anyone may read them; only a
# content manager writes them.
InquiryFieldPermission = ReadOnlyOrContentManager
