"""
This file contains all the APIs related to attendance model
"""

from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from rest_framework.views import APIView

from attendances.models import Attendance
from attendances.serializers import AttendanceSerializer
from attendances.services import create_attendance
from rosters.models import RosterUserSchedule
from users.permissions import IsStaff
from utils.files import ValidateFileSize
from utils.response import DefaultResponse


class CreateAttendanceAPI(APIView):
    """
    This API is used to create attendance for a staff member
    Response codes:
        201, 400, 404
    """

    permission_classes = (IsStaff,)

    class InputSerializer(serializers.Serializer):
        roster_user_schedule = serializers.IntegerField()
        image = serializers.ImageField(
            validators=[
                ValidateFileSize(max_file_size=Attendance.MAX_FILE_SIZE),
                FileExtensionValidator(
                    allowed_extensions=Attendance.FILE_EXTENSIONS_ALLOWED
                ),
            ]
        )

    OutputSerializer = AttendanceSerializer

    def get_queryset(self, user, roster_user_schedule_id):
        return RosterUserSchedule.objects.filter(
            date_deleted__isnull=True, id=roster_user_schedule_id, user=user
        )

    def post(self, request, *args, **kwargs):
        serializer = self.InputSerializer(data=request.data)
        if not serializer.is_valid():
            return DefaultResponse(
                errors=serializer.errors, status=HTTP_400_BAD_REQUEST
            )

        validated_data = serializer.validated_data

        roster_user_schedule = self.get_queryset(
            user=request.user,
            roster_user_schedule_id=validated_data["roster_user_schedule"],
        ).first()

        if not roster_user_schedule:
            return DefaultResponse(
                errors="No Schedule found for given schedule id",
                status=HTTP_404_NOT_FOUND,
            )

        success, attendance = create_attendance(**validated_data)
        if not success:
            return DefaultResponse(errors=attendance, status=HTTP_400_BAD_REQUEST)

        return DefaultResponse(
            data=self.OutputSerializer(instance=attendance).data,
            status=HTTP_201_CREATED,
        )
