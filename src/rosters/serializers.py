"""
This file contains all the model serializers for rosters module.
"""

from rest_framework import serializers

from rosters.models import Roster, RosterUserSchedule
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
