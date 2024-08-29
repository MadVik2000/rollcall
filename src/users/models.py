"""
This file contains all the models for users module.
"""

from uuid import uuid4

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

from utils.models import BaseModel


class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, password, **kwargs):
        email = self.normalize_email(email=email)
        user = self.model(email=email, first_name=first_name, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, first_name, password, **kwargs):
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)
        return self.create_user(
            email=email, first_name=first_name, password=password, **kwargs
        )


class User(AbstractUser):
    """
    This model is used to store all the details for a user.
    """

    username = None
    uuid = models.UUIDField(default=uuid4, primary_key=True)
    email = models.EmailField(max_length=256, unique=True)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name.strip()} {(self.last_name or '').strip()}".rstrip()


class UserRole(BaseModel):
    """
    This model is used to store all the roles associated with a user.
    """

    class Role(models.IntegerChoices):
        STAFF = 1
        MANAGER = 2

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    role = models.PositiveSmallIntegerField(choices=Role.choices)

    class Meta:
        verbose_name = "User Role"
        verbose_name_plural = "User Roles"
        constraints = [
            models.UniqueConstraint(
                fields=("user", "role"),
                name="user_role_unique_constraint",
                violation_error_message="User with this role already exists",
            )
        ]
