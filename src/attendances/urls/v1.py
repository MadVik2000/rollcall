"""
This file contains all the v1 urls used for attendance module
"""

from django.urls import path

from attendances.apis.v1 import attendance

urlpatterns = [
    path("", attendance.CreateAttendanceAPI.as_view(), name="attendance-create")
]
