"""
This file contains all the model admin configurations for attendances module
"""

from django.contrib import admin
from django.contrib.admin import ModelAdmin

from attendances.models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(ModelAdmin):
    list_display = ("id", "roster_user_schedule", "capture_image", "time")
    search_fields = (
        "roster_user_schedule__user__email",
        "roster_user_schedule__roster__title",
    )
    list_select_related = ("roster_user_schedule__user", "roster_user_schedule__roster")
