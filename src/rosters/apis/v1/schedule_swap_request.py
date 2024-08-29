"""
This file contains all the APIs related to schedule swap request model.
"""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from rest_framework.views import APIView

from rosters.models import RosterUserSchedule, ScheduleSwapRequest
from rosters.services import (
    bulk_create_roster_user_schedule,
    create_schedule_swap_request,
    update_schedule_swap_request,
)
from users.permissions import IsStaff
from utils.response import DefaultResponse, EmptyResponse
from rosters.serializers import ScheduleSwapRequestSerializer


class CreateScheduleSwapRequest(APIView):
    """
    This API is used to create a schedule swap request.
    Response Codes:
        201, 400, 404
    """

    permission_classes = (IsStaff,)

    class InputSerializer(serializers.Serializer):
        receiver = serializers.UUIDField()
        schedule = serializers.IntegerField()

    def get_queryset(self, user, schedule_id):
        return RosterUserSchedule.objects.filter(
            date_deleted__isnull=True, user=user, id=schedule_id
        )

    def post(self, request, *args, **kwargs):
        serializer = self.InputSerializer(data=request.data)
        if not serializer.is_valid():
            return DefaultResponse(
                errors=serializer.errors, status=HTTP_400_BAD_REQUEST
            )

        validated_data = serializer.validated_data

        if not self.get_queryset(
            user=request.user, schedule_id=validated_data["schedule"]
        ).exists():
            return DefaultResponse(
                errors="No schedule found for given data", status=HTTP_404_NOT_FOUND
            )

        success, schedule_swap_request = create_schedule_swap_request(
            sender=request.user, created_by=request.user, **validated_data
        )
        if not success:
            return DefaultResponse(
                errors=schedule_swap_request, status=HTTP_400_BAD_REQUEST
            )

        return EmptyResponse(status=HTTP_201_CREATED)


class ListScheduleSwapRequest(APIView):
    """
    This API is used to list all schedule swap requests received by a user.
    Response Codes:
        200
    """

    permission_classes = (IsStaff,)

    class OutputSerializer(ScheduleSwapRequestSerializer):
        request_date = serializers.SerializerMethodField()

        def get_request_date(self, instance):
            return instance.date_created

        class Meta:
            model = ScheduleSwapRequest
            fields = ("id","sender", "request_date")

    def get_queryset(self, user):
        return ScheduleSwapRequest.objects.filter(
            date_deleted__isnull=True,
            receiver=user,
            status=ScheduleSwapRequest.Status.PENDING,
        )

    def get(self, request, *args, **kwargs):
        return DefaultResponse(
            data=self.OutputSerializer(
                instance=self.get_queryset(user=request.user), many=True
            ).data,
            status=HTTP_200_OK,
        )


class AcceptRejectScheduleSwapRequest(APIView):
    """
    This API is used to accept or reject a schedule swap request.
    Response Codes:
        204, 400, 404
    """

    permission_classes = (IsStaff,)

    class InputSerializer(serializers.Serializer):
        swap_request_id = serializers.IntegerField()
        action = serializers.ChoiceField(
            choices=[
                ScheduleSwapRequest.Status.ACCEPTED.label,
                ScheduleSwapRequest.Status.REJECTED.label,
            ]
        )

        def validate_action(self, value):
            return getattr(ScheduleSwapRequest.Status, value.upper())

    def get_queryset(self, receiver, swap_request_id):
        return ScheduleSwapRequest.objects.filter(
            date_deleted__isnull=True,
            id=swap_request_id,
            sender_schedule__date_deleted__isnull=True,
            receiver=receiver,
            status=ScheduleSwapRequest.Status.PENDING,
        ).select_related("sender_schedule")

    def post(self, request, *args, **kwargs):
        serializer = self.InputSerializer(data=request.data)
        if not serializer.is_valid():
            return DefaultResponse(
                errors=serializer.errors, status=HTTP_400_BAD_REQUEST
            )

        validated_data = serializer.validated_data

        schedule_swap_request = self.get_queryset(
            receiver=request.user, swap_request_id=validated_data["swap_request_id"]
        ).first()
        if not schedule_swap_request:
            return DefaultResponse(
                errors="No swap request found with given data",
                status=HTTP_404_NOT_FOUND,
            )

        try:
            with transaction.atomic():
                success, swap_request = update_schedule_swap_request(
                    schedule_swap_request=schedule_swap_request,
                    status=validated_data["action"],
                    date_deleted=now(),
                )
                if not success:
                    raise ValidationError(swap_request)

                if swap_request.status == ScheduleSwapRequest.Status.ACCEPTED:
                    sender_schedule = schedule_swap_request.sender_schedule
                    receiver_schedule = RosterUserSchedule.objects.filter(
                        date_deleted__isnull=True,
                        user=request.user,
                        schedule_date=sender_schedule.schedule_date,
                    ).first()

                    if not receiver_schedule:
                        raise ValidationError("No schedule found for receiver")

                    new_schedule_data = [
                        {
                            "user": sender_schedule.user,
                            "schedule_date": receiver_schedule.schedule_date,
                            "start_time": receiver_schedule.start_time,
                            "end_time": receiver_schedule.end_time,
                        },
                        {
                            "user": receiver_schedule.user,
                            "schedule_date": sender_schedule.schedule_date,
                            "start_time": sender_schedule.start_time,
                            "end_time": sender_schedule.end_time,
                        },
                    ]
                    sender_schedule.date_deleted = now()
                    sender_schedule.updated_by = request.user

                    receiver_schedule.date_deleted = now()
                    receiver_schedule.updated_by = request.user

                    RosterUserSchedule.objects.bulk_update(
                        objs=[sender_schedule, receiver_schedule],
                        fields=["date_deleted", "updated_by"],
                    )

                    success, roster_user_schedules = bulk_create_roster_user_schedule(
                        roster=sender_schedule.roster,
                        user_schedule_data=new_schedule_data,
                        created_by=request.user,
                    )
                    if not success:
                        raise ValidationError(roster_user_schedules)

        except ValidationError as error:
            return DefaultResponse(errors=str(error), status=HTTP_400_BAD_REQUEST)

        return EmptyResponse()
