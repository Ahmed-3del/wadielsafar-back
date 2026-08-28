from django.contrib.auth.models import AbstractUser
from django.db import models

from common.constants import RoleChoices


class User(AbstractUser):
    # Email is the login identifier the frontends authenticate with; username
    # is kept only because AbstractUser requires it, not for login.
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.SALES,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email
