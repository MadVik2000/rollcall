"""
This file contains all the model admin configurations for users module
"""

from django.contrib import admin
from django.contrib.admin import ModelAdmin

from users.models import User, UserRole


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ("uuid", "email", "first_name", "last_name")
    search_fields = ("email", "first_name", "last_name")


@admin.register(UserRole)
class UserRoleAdmin(ModelAdmin):
    list_display = ("user", "role")
    search_fields = ("user__email",)
    list_select_related = ("user",)
    list_filter = ("role",)
    autocomplete_fields = ("user",)
