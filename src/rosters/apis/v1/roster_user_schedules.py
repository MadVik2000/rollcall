"""
This file contains all the APIs related to roster user schedules model.
"""

from rest_framework import serializers
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from rosters.models import Roster, RosterManager
from rosters.serializers import RosterUserScheduleSerializer
from rosters.services import bulk_create_roster_user_schedule
from users.permissions import IsManager
from utils.response import DefaultResponse


class BulkCreateRosterUserScheduleAPI(APIView):
    """
    This API is used to create multiple user schedules within a single roster.
    Response Codes:
        201, 400
    """

    permission_classes = (IsManager,)

    class InputSerializer(serializers.Serializer):

        class UserScheduleSerializer(serializers.Serializer):
            user = serializers.UUIDField()
            schedule_date = serializers.DateField()
            start_time = serializers.DateTimeField()
            end_time = serializers.DateTimeField()

            def validate(self, attrs):
                if attrs["start_time"] >= attrs["end_time"]:
                    raise serializers.ValidationError(
                        "End time must be greater than start time"
                    )

                return super().validate(attrs)

        user_schedules = UserScheduleSerializer(many=True, min_length=1)

    OutputSerializer = RosterUserScheduleSerializer

    def get_queryset(self, user, roster_id):
        return RosterManager.objects.filter(
            roster_id=roster_id, manager=user, date_deleted__isnull=True
        )

    def post(self, request, roster_id, *args, **kwargs):
        serializer = self.InputSerializer(data=request.data)
        if not serializer.is_valid():
            return DefaultResponse(
                errors=serializer.errors, status=HTTP_400_BAD_REQUEST
            )

        roster = Roster.objects.filter(
            id=roster_id, is_active=True, date_deleted__isnull=True
        ).first()
        if not roster:
            return DefaultResponse(
                errors="User schedules can only be created for an active roster",
                status=HTTP_400_BAD_REQUEST,
            )

        if not self.get_queryset(user=request.user, roster_id=roster_id).first():
            return DefaultResponse(
                errors="Only roster manager can add user schedules",
                status=HTTP_400_BAD_REQUEST,
            )

        success, user_schedules = bulk_create_roster_user_schedule(
            roster=roster,
            user_schedule_data=serializer.validated_data["user_schedules"],
            created_by=request.user,
        )
        if not success:
            return DefaultResponse(errors=user_schedules, status=HTTP_400_BAD_REQUEST)

        return DefaultResponse(
            data=self.OutputSerializer(instance=user_schedules, many=True).data,
            status=HTTP_201_CREATED,
        )
