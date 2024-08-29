"""
This file contains all the v1 urls used for users module
"""

from django.urls import path

from users.apis.v1 import users

urlpatterns = [
    path("login/", users.UserLoginAPI.as_view(), name="user-login"),
    path("staff/", users.ListStaffUserAPI.as_view(), name="staff-list"),
]
