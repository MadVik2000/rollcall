"""
This file contains all the utilities related to files
"""

from django.core.exceptions import ValidationError
from django.core.files import File
from django.utils.deconstruct import deconstructible


@deconstructible
class RenameFile:
    def __init__(self, pattern):
        self.pattern = pattern

    def __call__(self, instance, filename):
        extension = filename.split(".")[-1]
        return self.pattern.format(instance=instance, extension=extension)


@deconstructible
class ValidateFileSize:
    """
    Used to validate file size
    """

    def __init__(self, max_file_size) -> None:
        self.file_size = max_file_size

    def __call__(self, file: File) -> None:
        file_size = file.size
        if file_size > self.file_size * 1024 * 1024:
            raise ValidationError(f"Max file size limit is {file_size}.")
