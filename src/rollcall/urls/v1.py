"""
This file contains all the url routes for version v1
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("users/", include("users.urls.v1")),
    path("rosters/", include("rosters.urls.v1")),
    path("attendance/", include("attendances.urls.v1")),
]
