"""
This file contains all the APIs related to rosters model.
"""

from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rosters.services import create_roster, create_roster_manager
from users.permissions import IsManager

from utils.response import DefaultResponse, EmptyResponse


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
