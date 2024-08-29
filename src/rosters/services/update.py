"""
This file contains all the create services for rosters module.
"""

from datetime import date, datetime
from typing import Optional, Tuple, Union

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from rosters.models import RosterUserSchedule, ScheduleSwapRequest

User = get_user_model()


def update_roster_user_schedule(
    roster_user_schedule: RosterUserSchedule,
    schedule_date: date = None,
    start_time: datetime = None,
    end_time: datetime = None,
    updated_by: Optional[User] = None,  # type: ignore
) -> Tuple[bool, Union[str, RosterUserSchedule]]:
    """
    This service is used to update a roster user schedule instance.
    """

    if not isinstance(roster_user_schedule, RosterUserSchedule):
        return False, "roster_user_schedule must be an instance of RosterUserSchedule"

    updation_data = {
        "schedule_date": schedule_date,
        "start_time": start_time,
        "end_time": end_time,
    }

    update_fields = []

    for data, value in updation_data.items():
        if not value:
            continue

        setattr(roster_user_schedule, data, value)
        update_fields.append(data)

    if not update_fields:
        return False, "Atleast one field must be updated."

    roster_user_schedule.updated_by = updated_by
    update_fields.extend(["date_updated", "updated_by"])

    try:
        roster_user_schedule.save(update_fields=update_fields)
    except (ValidationError, IntegrityError) as error:
        return False, str(error)

    return True, roster_user_schedule


def update_schedule_swap_request(
    schedule_swap_request: ScheduleSwapRequest,
    status: ScheduleSwapRequest.Status,
    date_deleted: Optional[datetime] = None,
) -> Tuple[bool, Union[str, ScheduleSwapRequest]]:
    """
    This service is used to update a schedule swap request instance.
    """

    schedule_swap_request.status = status
    if date_deleted:
        schedule_swap_request.date_deleted = date_deleted

    try:
        schedule_swap_request.save()
    except ValidationError as error:
        return False, str(error)

    return True, schedule_swap_request
