"""
This file contains all the models related to rosters module.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now

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
                violation_error_message="User is already manager for this roster.",
            )
        ]

    def validate_manager(self):
        if not UserRole.objects.filter(
            user_id=self.manager.uuid,
            role=UserRole.Role.MANAGER,
            date_deleted__isnull=True,
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
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

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
                violation_error_message="Staff user can only have one active schedule on a day.",
            )
        ]

    def validate_user(self):
        if not UserRole.objects.filter(
            user_id=self.user.uuid,
            role=UserRole.Role.STAFF,
            date_deleted__isnull=True,
        ).exists():
            raise ValidationError(
                "Schedule can be added for users with staff role only."
            )

    def validate_roster(self):
        if not self.roster.is_active:
            raise ValidationError(
                "Cannot add roster user schedule for an inactive roster."
            )

    def validate_time_fields(self):
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be greater than start time")

        if self.schedule_date != self.start_time.date():
            raise ValidationError("Schedule date and start time date should be same")

        if self.end_time - self.start_time < timedelta(hours=6):
            raise ValidationError("A schedule must be atleast 6 hours long.")

    def clean(self) -> None:
        self.validate_time_fields()
        return super().clean()

    def full_clean(self, *args, **kwargs) -> None:
        self.validate_user()
        self.validate_roster()
        return super().full_clean(*args, **kwargs)


class ScheduleSwapRequest(BaseModel):
    """
    This model is used to store user schedule swap requests.
    """

    class Status(models.IntegerChoices):
        PENDING = 1
        ACCEPTED = 2
        REJECTED = 3

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="receiver"
    )
    status = models.PositiveSmallIntegerField(
        choices=Status.choices, default=Status.PENDING
    )
    sender_schedule = models.ForeignKey(RosterUserSchedule, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.sender} request to {self.receiver}"

    class Meta:
        verbose_name = "Schedule Swap Request"
        verbose_name_plural = "Schedule Swap Requests"
        constraints = [
            models.UniqueConstraint(
                fields=["sender", "receiver", "sender_schedule"],
                name="sender_receiver_sender_schedule_unique_constraint",
                condition=models.Q(date_deleted__isnull=True),
                violation_error_message="A swap request already exists.",
            )
        ]

    def validate_user(self):
        if ScheduleSwapRequest.objects.filter(
            date_deleted__isnull=True,
            receiver=self.sender,
            sender=self.receiver,
            sender_schedule__schedule_date=self.sender_schedule.schedule_date,
        ).exists():
            raise ValidationError(
                "Already received a request from receiver to swap given date schedule"
            )

    def validate_sender_schedule(self):
        if not self.pk and self.sender_schedule.date_deleted:
            raise ValidationError("Cannot create a swap request for inactive schedule.")

        if self.sender_schedule.user != self.sender:
            raise ValidationError("Sender and sender schedule should be same")

        if self.sender == self.receiver:
            raise ValidationError("Sender and receiver cannot be same")

        if (
            self.sender_schedule.start_time - timedelta(hours=1) <= now()
            and self.status != self.Status.REJECTED
        ):
            raise ValidationError(
                "Cannot create/update swap request an hour before schedule start time"
            )

        if not RosterUserSchedule.objects.filter(
            date_deleted__isnull=True,
            user=self.receiver,
            schedule_date=self.sender_schedule.schedule_date,
        ).exists():
            raise ValidationError(
                f"Receiver does not have any active schedule for the date {self.sender_schedule.schedule_date}"
            )

    def validate_status(self):
        if not self.pk and self.status != self.Status.PENDING:
            raise ValidationError(
                "Swap request can only be created with pending status"
            )

    def clean(self) -> None:
        self.validate_status()
        return super().clean()

    def full_clean(self, *args, **kwargs):
        self.validate_user()
        self.validate_sender_schedule()
        return super().full_clean(*args, **kwargs)
