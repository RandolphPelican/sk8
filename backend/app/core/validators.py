from app.core.config import settings
from app.core.exceptions import ClipTooLongException, ClipTooLargeException


def validate_clip_duration(duration_seconds: float) -> None:
    """Validate clip duration is within limits"""
    if duration_seconds > settings.MAX_CLIP_DURATION_SECONDS:
        raise ClipTooLongException(duration_seconds, settings.MAX_CLIP_DURATION_SECONDS)


def validate_clip_size(size_bytes: int) -> None:
    """Validate clip file size is within limits"""
    size_mb = size_bytes / (1024 * 1024)
    if size_mb > settings.MAX_CLIP_SIZE_MB:
        raise ClipTooLargeException(size_mb, settings.MAX_CLIP_SIZE_MB)


def validate_gps_coordinates(lat: float, lng: float) -> None:
    """Basic GPS coordinate validation"""
    if not (-90 <= lat <= 90):
        raise ValueError("Latitude must be between -90 and 90")
    if not (-180 <= lng <= 180):
        raise ValueError("Longitude must be between -180 and 180")
