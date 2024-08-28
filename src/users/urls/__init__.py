"""
This file contains all the v1 urls used for users module
"""

from django.urls import include, path

urlpatterns = [
    path("v1/", include("users.urls.v1")),
]
