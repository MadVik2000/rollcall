"""
This file contains all the APIs related to rosters model.
"""

from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.views import APIView
from rosters.services import create_roster, create_roster_manager
from users.permissions import IsManager
from rosters.models import Roster, RosterManager
from utils.response import DefaultResponse, EmptyResponse
from rosters.serializers import RosterSerializer


class CreateRosterAPI(APIView):
    """
    This API is used to create a roster
    Response Codes:
        201, 400
    """

    permission_classes = (IsManager,)

    class InputSerializer(serializers.Serializer):
        title = serializers.CharField(max_length=256)

    def post(self, request, *args, **kwargs):
        serializer = self.InputSerializer(data=request.data)
        if not serializer.is_valid():
            return DefaultResponse(data=serializer.errors, status=HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        try:
            with transaction.atomic():
                success, roster = create_roster(
                    title=validated_data["title"],
                    is_active=True,
                    created_by=request.user,
                )
                if not success:
                    raise ValidationError(message=roster)

                success, roster_manager = create_roster_manager(
                    roster=roster,
                    manager=request.user,
                    created_by=request.user,
                )
                if not success:
                    raise ValidationError(message=roster_manager)

        except ValidationError as error:
            return DefaultResponse(errors=str(error), status=HTTP_400_BAD_REQUEST)

        return EmptyResponse(status=HTTP_201_CREATED)


class ListRosterAPI(APIView):
    """
    This API is used to list all the rosters for a manager.
    Response Codes:
        200
    """

    permission_classes = (IsManager,)

    OutputSerializer = RosterSerializer

    def get_queryset(self, user):
        return Roster.objects.filter(
            date_deleted__isnull=True,
            id__in=RosterManager.objects.filter(manager=user).values_list(
                "roster_id", flat=True
            ),
        )

    def get(self, request, *args, **kwargs):
        return DefaultResponse(
            data=self.OutputSerializer(
                instance=self.get_queryset(user=request.user), many=True
            ).data,
            status=HTTP_200_OK,
        )
