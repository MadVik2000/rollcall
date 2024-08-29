"""
This file contains all the model serializers for rosters module.
"""

from rest_framework import serializers

from rosters.models import Roster, RosterUserSchedule, ScheduleSwapRequest
from users.serializers import UserSerializer


class RosterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roster
        exclude = Roster.LOG_FIELDS


class RosterUserScheduleSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = RosterUserSchedule
        exclude = RosterUserSchedule.LOG_FIELDS


class ScheduleSwapRequestSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    receiver = UserSerializer()
    status = serializers.SerializerMethodField()

    def get_status(self, instance):
        return ScheduleSwapRequest.Status(instance.status).label

    class Meta:
        model = ScheduleSwapRequest
        exclude = ScheduleSwapRequest.LOG_FIELDS
