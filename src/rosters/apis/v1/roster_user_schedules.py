"""
This file contains all the APIs related to roster user schedules model.
"""

from rest_framework import serializers
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from rest_framework.views import APIView

from rosters.models import Roster, RosterManager, RosterUserSchedule
from rosters.serializers import RosterUserScheduleSerializer
from rosters.services import (
    bulk_create_roster_user_schedule,
    update_roster_user_schedule,
)
from users.models import UserRole
from users.permissions import IsManager, IsStaff
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


class UpdateRosterUserScheduleAPI(APIView):
    """
    This API is used to update a user schedule.
    Response Code:
        200, 400, 404
    """

    permission_classes = (IsManager,)

    class InputSerializer(serializers.Serializer):
        schedule_date = serializers.DateField()
        start_time = serializers.DateTimeField()
        end_time = serializers.DateTimeField()

        def validate(self, attrs):
            if attrs["start_time"] >= attrs["end_time"]:
                raise serializers.ValidationError(
                    "End time must be greater than start time"
                )

            return super().validate(attrs)

    OutputSerializer = RosterUserScheduleSerializer

    def get_queryset(self, manager, user_schedule_id):
        return RosterUserSchedule.objects.filter(
            date_deleted__isnull=True,
            id=user_schedule_id,
            roster__rostermanager__manager=manager,
        )

    def put(self, request, user_schedule_id, *args, **kwargs):
        serializer = self.InputSerializer(data=request.data)
        if not serializer.is_valid():
            return DefaultResponse(
                errors=serializer.errors, status=HTTP_400_BAD_REQUEST
            )

        user_schedule = self.get_queryset(
            manager=request.user, user_schedule_id=user_schedule_id
        ).first()
        if not user_schedule:
            return DefaultResponse(
                errors="No User Schedule Found", status=HTTP_404_NOT_FOUND
            )

        success, user_schedule = update_roster_user_schedule(
            roster_user_schedule=user_schedule,
            updated_by=request.user,
            **serializer.validated_data
        )

        if not success:
            return DefaultResponse(errors=user_schedule, status=HTTP_400_BAD_REQUEST)

        return DefaultResponse(
            data=self.OutputSerializer(instance=user_schedule).data,
            status=HTTP_202_ACCEPTED,
        )


class ListRosterUserScheduleAPI(APIView):
    """
    This API is used to list all the user schedules associated with a roster.
    In case a staff user accesses this API, he/she would only be able to access
    their own schedule(s) list.

    Response Codes:
        200
    """

    permission_classes = (IsManager | IsStaff,)

    OutputSerializer = RosterUserScheduleSerializer

    def get_queryset(self, roster_id):
        return RosterUserSchedule.objects.filter(
            date_deleted__isnull=True, roster_id=roster_id
        )

    def get(self, request, roster_id, *args, **kwargs):
        user_schedules = self.get_queryset(roster_id=roster_id)
        if not request.user.userrole_set.filter(role=UserRole.Role.MANAGER).exists():
            user_schedules = user_schedules.filter(user=request.user)

        return DefaultResponse(
            data=self.OutputSerializer(instance=user_schedules, many=True).data,
            status=HTTP_200_OK,
        )
