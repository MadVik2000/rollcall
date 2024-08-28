"""
This file contains all the model serializers for rosters module.
"""

from rest_framework import serializers

from rosters.models import Roster


class RosterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roster
        exclude = Roster.LOG_FIELDS
