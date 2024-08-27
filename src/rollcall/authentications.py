"""
This file contains all the custom authentications for rollcall.
"""

from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from utils.helpers import decode_user_token

User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    """
    This class is used for jwt token authentication.
    """

    def authenticate(self, request):
        jwt_token = request.META.get("HTTP_AUTHORIZATION", b"").split()

        if not jwt_token or jwt_token[0].lower() != "bearer":
            return None

        if len(jwt_token) == 1:
            raise AuthenticationFailed("Invalid token header. No credentials provided.")
        elif len(jwt_token) > 2:
            raise AuthenticationFailed(
                "Invalid token header. Token string should not contain spaces."
            )

        try:
            payload = decode_user_token(token=jwt_token[1])
            user = User.objects.get(uuid=payload["user_id"])
            if not user:
                raise Exception("User not found")
        except Exception as error:
            raise AuthenticationFailed(error)

        return user, payload

    def authenticate_header(self, request):
        return "Bearer"
