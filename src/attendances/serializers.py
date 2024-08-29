"""
This file contains all the model serializers for attendance module.
"""

from rest_framework import serializers

from attendances.models import Attendance
from rosters.serializers import RosterUserScheduleSerializer


class AttendanceSerializer(serializers.ModelSerializer):
    roster_user_schedule = RosterUserScheduleSerializer()

    class Meta:
        model = Attendance
        exclude = Attendance.LOG_FIELDS
