"""
This file contains all the models related to attendances module.
"""

from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.timezone import now

from rosters.models import RosterUserSchedule
from utils.files import RenameFile, ValidateFileSize
from utils.models import BaseModel

FILE_STORAGE = FileSystemStorage(location=settings.MEDIA_ROOT)


class Attendance(BaseModel):
    """
    This model is used to store attendance for a user schedule.
    """

    MAX_FILE_SIZE = 10  # in Mb
    FILE_EXTENSIONS_ALLOWED = ("jpeg", "jpg", "png")

    roster_user_schedule = models.OneToOneField(
        RosterUserSchedule, on_delete=models.PROTECT
    )
    capture_image = models.ImageField(
        storage=FILE_STORAGE,
        upload_to=RenameFile("files/attendance/{instance.roster_user_schedule.user_id}/{instance.date_created}.{extension}"
        ),
        validators=[
            ValidateFileSize(max_file_size=MAX_FILE_SIZE),
            FileExtensionValidator(allowed_extensions=FILE_EXTENSIONS_ALLOWED),
        ],
        null=True,
        blank=True,
    )

    time = models.DateTimeField(default=now)

    class Meta:
        verbose_name = "Attendance"
        verbose_name_plural = "Attendances"

    def __str__(self):
        return f"{self.roster_user_schedule}"

    def validate_time(self):
        if not (
            self.roster_user_schedule.start_time - timedelta(hours=1)
            <= self.time
            <= self.roster_user_schedule.start_time + timedelta(hours=1)
        ):
            raise ValidationError(
                "Attendance can only be marked within one hour of the schedule start time."
            )

    def full_clean(self, *args, **kwargs):
        self.validate_time()
        return super().full_clean(*args, **kwargs)
