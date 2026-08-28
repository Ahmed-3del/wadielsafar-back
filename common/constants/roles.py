from django.db import models


class RoleChoices(models.TextChoices):
    SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"
    ADMIN = "ADMIN", "Admin"
    EDITOR = "EDITOR", "Editor"
    SALES = "SALES", "Sales"


# Roles that may manage catalog content (destinations, packages, visas, etc.)
STAFF_CONTENT_ROLES = (RoleChoices.SUPER_ADMIN, RoleChoices.ADMIN, RoleChoices.EDITOR)

# Roles that may view/manage leads and inquiries
STAFF_SALES_ROLES = (RoleChoices.SUPER_ADMIN, RoleChoices.ADMIN, RoleChoices.SALES)

# Roles considered "staff" for the read-only users directory
STAFF_ROLES = (RoleChoices.SUPER_ADMIN, RoleChoices.ADMIN, RoleChoices.EDITOR, RoleChoices.SALES)
