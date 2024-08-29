"""
This file contains all the APIs related to users module.
"""

from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from users.models import UserRole
from users.permissions import IsManager
from users.serializers import UserSerializer
from utils.helpers import generate_user_token
from utils.response import DefaultResponse

User = get_user_model()


class UserLoginAPI(APIView):
    """
    This API is used for login of user.
    It accepts a user email and password and return
    a jwt token.

    Response Codes:
        200, 404
    """

    permission_classes = (AllowAny,)

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        password = serializers.CharField()

    def post(self, request, *args, **kwargs):
        serializer = self.InputSerializer(data=request.data)
        if not serializer.is_valid():
            return DefaultResponse(
                errors=serializer.errors, status=HTTP_400_BAD_REQUEST
            )

        user = authenticate(**serializer.validated_data)
        if not user:
            return DefaultResponse(
                errors="No active account found with the given credentials.",
                status=HTTP_400_BAD_REQUEST,
            )

        return DefaultResponse(
            data={"access_token": generate_user_token(user=user)}, status=HTTP_200_OK
        )


class ListStaffUserAPI(APIView):
    """
    This API is used to list all the available staff users.
    Response Codes:
        200
    """

    permission_classes = (IsManager,)

    OutputSerializer = UserSerializer

    def get_queryset(self):
        return User.objects.filter(
            uuid__in=UserRole.objects.filter(role=UserRole.Role.STAFF).values_list(
                "user_id", flat=True
            )
        )

    def get(self, request, *args, **kwargs):
        return DefaultResponse(
            data=self.OutputSerializer(instance=self.get_queryset(), many=True).data,
            status=HTTP_200_OK,
        )
