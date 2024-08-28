"""
This file contains all the models related to rosters module.
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from users.models import UserRole
from utils.models import BaseModel

User = get_user_model()


class Roster(BaseModel):
    """
    This model is used to store a roster detail.
    """

    title = models.CharField(max_length=256)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Roster"
        verbose_name_plural = "Rosters"


class RosterManager(BaseModel):
    """
    This model is used to store mapping between a roster and its associated
    managers.
    """

    roster = models.ForeignKey(Roster, on_delete=models.CASCADE)
    manager = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.roster} - {self.manager}"

    class Meta:
        verbose_name = "Roster Manager"
        verbose_name_plural = "Roster Managers"
        constraints = [
            models.UniqueConstraint(
                fields=["roster", "manager"],
                name="roster_manager_unique_constraint",
            )
        ]

    def validate_manager(self):
        if not UserRole.objects.filter(
            user_id=self.manager.uuid,
            role=UserRole.Role.MANAGER,
            date_deleted__isnull=False,
        ).exists():
            raise ValidationError(
                "Only users with managers role can be added as a roster manager"
            )

    def full_clean(self, *args, **kwargs):
        self.validate_manager()
        return super().full_clean(*args, **kwargs)


class RosterUserSchedule(BaseModel):
    """
    This model is used to store all the schedule for a user related to a roster.
    """

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    roster = models.ForeignKey(Roster, on_delete=models.CASCADE)
    schedule_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.roster} - {self.user}"

    class Meta:
        verbose_name = "Roster User Schedule"
        verbose_name_plural = "Roster User Schedules"
        constraints = [
            models.UniqueConstraint(
                fields=["roster", "user", "schedule_date"],
                name="roster_user_schedule_date_unique_constraint",
                condition=models.Q(date_deleted__isnull=True),
            )
        ]

    def validate_user(self):
        if not UserRole.objects.filter(
            user_id=self.user.uuid,
            role=UserRole.Role.STAFF,
            date_deleted__isnull=False,
        ).exists():
            raise ValidationError(
                "Schedule can be added for users with staff role only."
            )

    def validate_time_fields(self):
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be greater than start time")

    def clean(self) -> None:
        self.validate_time_fields()
        return super().clean()

    def full_clean(self, *args, **kwargs) -> None:
        self.validate_user()
        return super().full_clean(*args, **kwargs)
