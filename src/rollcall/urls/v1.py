"""
This file contains all the url routes for version v1
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("users/", include("users.urls.v1")),
]
