"""
This file contains all the v1 urls used for rosters module
"""

from django.urls import path

from rosters.apis.v1 import roster_user_schedules, rosters, schedule_swap_request

urlpatterns = [
    path("", rosters.CreateRosterAPI.as_view(), name="roster-create"),
    path("list/", rosters.ListRosterAPI.as_view(), name="roster-list"),
    path(
        "<int:roster_id>/schedule/",
        roster_user_schedules.BulkCreateRosterUserScheduleAPI.as_view(),
        name="schedule-create",
    ),
    path(
        "schedule/<int:user_schedule_id>/",
        roster_user_schedules.UpdateRosterUserScheduleAPI.as_view(),
        name="schedule-create",
    ),
    path(
        "<int:roster_id>/schedule/list/",
        roster_user_schedules.ListRosterUserScheduleAPI.as_view(),
        name="schedule-list",
    ),
    path(
        "schedule/swap/",
        schedule_swap_request.CreateScheduleSwapRequest.as_view(),
        name="swap-request-create",
    ),
    path(
        "schedule/swap/list/",
        schedule_swap_request.ListScheduleSwapRequest.as_view(),
        name="swap-request-list",
    ),
    path(
        "schedule/swap/action/",
        schedule_swap_request.AcceptRejectScheduleSwapRequest.as_view(),
        name="swap-request-action",
    ),
]
