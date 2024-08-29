"""
This file contains all the model admin configurations for rosters module
"""

from django.contrib import admin
from django.contrib.admin import ModelAdmin

from rosters.models import (
    Roster,
    RosterManager,
    RosterUserSchedule,
    ScheduleSwapRequest,
)


@admin.register(Roster)
class RosterAdmin(ModelAdmin):
    list_display = ("id", "title", "is_active")
    search_fields = ("title",)
    list_filter = ("is_active",)


@admin.register(RosterUserSchedule)
class RosterUserScheduleAdmin(ModelAdmin):
    list_display = (
        "id",
        "roster",
        "user",
        "schedule_date",
        "start_time",
        "end_time",
    )
    list_select_related = ("roster", "user")
    search_fields = ("roster__title", "user__email")
    list_filter = ("roster__title",)
    autocomplete_fields = ("roster", "user")


@admin.register(RosterManager)
class RosterManagerAdmin(ModelAdmin):
    list_display = ("id", "roster", "manager")
    list_select_related = ("roster", "manager")
    search_fields = ("roster__title", "manager__email")
    autocomplete_fields = ("roster", "manager")


@admin.register(ScheduleSwapRequest)
class ScheduleSwapRequestAdmin(ModelAdmin):
    list_display = ("id", "sender", "receiver", "status")
    search_fields = (
        "sender__email",
        "receiver__email",
        "sender_schedule__roster__title",
    )
    list_filter = ("status",)
    list_select_related = ("sender", "receiver", "sender_schedule__roster")
    autocomplete_fields = ("sender", "receiver", "sender_schedule")
