"""
This file contains all the v1 urls used for rosters module
"""

from django.urls import path

from rosters.apis.v1 import rosters

urlpatterns = [
    path("", rosters.CreateRosterAPI.as_view(), name="roster-list"),
]
