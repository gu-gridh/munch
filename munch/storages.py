"""
Storage Classes

Custom file storage classes for handling original and IIIF files.
Provides specialized storage for digital humanities projects.
"""

from django.core.files.storage import FileSystemStorage
from django.contrib.staticfiles.storage import ManifestStaticFilesStorage
from django.conf import settings


class ForgivingManifestStaticFilesStorage(ManifestStaticFilesStorage):
    """ManifestStaticFilesStorage that silently skips missing referenced files
    (e.g. .map sourcemap files referenced in minified JS/CSS)."""

    def hashed_name(self, name, content=None, filename=None):
        try:
            return super().hashed_name(name, content, filename)
        except ValueError:
            return name


class OriginalFileStorage(FileSystemStorage):
    """Storage for original uploaded files"""

    def __init__(self) -> None:
        location = settings.MEDIA_ROOT
        base_url = getattr(settings, 'ORIGINAL_URL', settings.MEDIA_URL)
        super().__init__(location, base_url)


class IIIFFileStorage(FileSystemStorage):
    """Storage for IIIF-processed files"""

    def __init__(self) -> None:
        location = settings.MEDIA_ROOT
        base_url = getattr(settings, 'IIIF_URL', settings.MEDIA_URL)
        super().__init__(location, base_url)
