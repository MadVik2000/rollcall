"""
This file contains all the utilities related to API response.
"""

from typing import Any, Optional

from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT


class DefaultResponse(Response):
    """
    Custom response class that returns data and errors encapsulated under a single base data object.
    """

    def __init__(
        self, *, data: Optional[Any] = None, errors: Optional[Any] = None, **kwargs
    ):
        if isinstance(data, str):
            data = {"message": data}

        if isinstance(errors, str):
            errors = {"message": errors}

        super().__init__(data={"data": data, "errors": errors}, **kwargs)


class EmptyResponse(Response):
    """
    Custom response class that return no data.
    """

    def __init__(self, *, status: Optional[int] = HTTP_204_NO_CONTENT, **kwargs):
        super().__init__(status=status, **kwargs)
