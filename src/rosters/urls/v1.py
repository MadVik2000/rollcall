"""
This file contains all the v1 urls used for rosters module
"""

from django.urls import path

from rosters.apis.v1 import roster_user_schedules, rosters

urlpatterns = [
    path("", rosters.CreateRosterAPI.as_view(), name="roster-create"),
    path("list/", rosters.ListRosterAPI.as_view(), name="roster-list"),
    path(
        "<int:roster_id>/schedule/",
        roster_user_schedules.BulkCreateRosterUserScheduleAPI.as_view(),
        name="schedule-create",
    ),
    path(
        "<int:roster_id>/schedule/list/",
        roster_user_schedules.ListRosterUserScheduleAPI.as_view(),
        name="schedule-list",
    ),
]
