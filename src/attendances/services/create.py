"""
This file contains all the create services for attendance module.
"""

from typing import Optional, Tuple, Union

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile

from attendances.models import Attendance
from rosters.models import RosterUserSchedule

User = get_user_model()


def create_attendance(
    roster_user_schedule: Union[int, RosterUserSchedule],
    image: ImageFile,
    created_by: Optional[User] = None,  # type: ignore
) -> Tuple[bool, Union[str, Attendance]]:
    """
    This service is used to create an attendance instance
    """
    attendance = Attendance(
        roster_user_schedule_id=(
            roster_user_schedule.id
            if isinstance(roster_user_schedule, RosterUserSchedule)
            else roster_user_schedule
        ),
        capture_image=image,
        created_by=created_by,
    )

    try:
        attendance.save()
    except ValidationError as error:
        return False, str(error)

    return True, attendance
