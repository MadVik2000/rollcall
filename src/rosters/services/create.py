"""
This file contains all the create services for rosters module.
"""

from datetime import date, datetime
from typing import List, Optional, Tuple, TypedDict, Union
from uuid import UUID

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.timezone import now

from rosters.models import Roster, RosterManager, RosterUserSchedule
from users.models import UserRole

User = get_user_model()


class RosterUserScheduleData(TypedDict):
    user: Union[int, User]  # type: ignore
    schedule_date: date
    start_time: datetime
    end_time: datetime


def create_roster(
    title: str, is_active: bool = False, created_by: Optional[User] = None  # type: ignore
) -> Tuple[bool, Union[str, Roster]]:
    """
    This service is used to create a roster.
    """
    roster = Roster(title=title, is_active=is_active, created_by=created_by)

    try:
        roster.save()
    except ValidationError as error:
        return False, str(error)

    return True, roster


def create_roster_manager(
    roster: Union[Roster, int],
    manager: Union[User, UUID],  # type: ignore
    created_by: Optional[User] = None,  # type: ignore
) -> Tuple[bool, Union[str, RosterManager]]:
    """
    This service is used to create a roster manager.
    """

    roster_manager = RosterManager(
        roster_id=(roster.id if isinstance(roster, Roster) else roster),
        manager_id=manager.uuid if isinstance(manager, User) else manager,
        created_by=created_by,
    )

    try:
        roster_manager.save()
    except ValidationError as error:
        return False, str(error)

    return True, roster_manager


def bulk_create_roster_user_schedule(
    roster: Roster,
    user_schedule_data: List[RosterUserScheduleData],
    created_by: Optional[User] = None,  # type: ignore
) -> Tuple[bool, Union[str, List[RosterUserSchedule]]]:
    """
    This service is used to bulk create roster user schedules.
    """

    if not roster.is_active:
        return False, "Cannot add roster user schedule for an inactive roster."

    users = {
        (
            roster_user_schedule["user"].uuid
            if isinstance(roster_user_schedule["user"], User)
            else roster_user_schedule["user"]
        )
        for roster_user_schedule in user_schedule_data
    }

    if (
        len(users)
        != UserRole.objects.filter(
            user_id__in=users,
            role=UserRole.Role.STAFF,
            date_deleted__isnull=True,
        ).count()
    ):
        return False, "All users must be staff members"

    roster_user_schedules = []

    try:
        for roster_user_schedule_data in user_schedule_data:
            roster_user_schedule = RosterUserSchedule(
                roster_id=roster.id,
                user_id=(
                    roster_user_schedule_data["user"].uuid
                    if isinstance(roster_user_schedule_data["user"], User)
                    else roster_user_schedule_data["user"]
                ),
                schedule_date=roster_user_schedule_data["schedule_date"],
                start_time=roster_user_schedule_data["start_time"],
                end_time=roster_user_schedule_data["end_time"],
                created_by=created_by,
            )

            roster_user_schedule.clean_fields(exclude=["roster", "user", "created_by"])
            roster_user_schedule.clean()
            roster_user_schedules.append(roster_user_schedule)

        roster_user_schedules = RosterUserSchedule.objects.bulk_create(
            objs=roster_user_schedules
        )
    except (ValidationError, IntegrityError) as error:
        return False, str(error)

    return True, roster_user_schedules
