"""
This file contains all the create services for rosters module.
"""

from typing import List, Optional, Tuple, Type, Union
from uuid import UUID

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from rosters.models import Roster, RosterManager

User = get_user_model()


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
