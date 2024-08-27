"""
This file contains all the helper utilities.
"""

from datetime import timedelta

import jwt
from django.conf import settings
from django.utils.timezone import now

from users.models import User


def generate_user_token(user: User):
    """
    This method is used to generate a jwt token for a user
    """

    payload = {
        "user_id": str(user.uuid),
        "iat": now(),
        "exp": now() + timedelta(days=3),
        "iss": "RollCall_Backend",
        "aud": "EndUser",
    }

    token = jwt.encode(payload=payload, key=settings.SECRET_KEY, algorithm="HS256")
    return token


def decode_user_token(token: str):
    """
    This method is used to decode a jwt token
    """

    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.SECRET_KEY,
            algorithms="HS256",
            issuer="RollCall_Backend",
            audience="EndUser",
        )
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as error:
        raise Exception(
            "Token Expired"
            if isinstance(error, jwt.ExpiredSignatureError)
            else "Invalid Token"
        )
