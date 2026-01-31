#!/bin/bash

echo "Adding error handling and validation..."

# Create custom exceptions
cat > app/core/exceptions.py << 'EOF'
from fastapi import HTTPException, status


class SK8Exception(HTTPException):
    """Base exception for SK8 app"""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class NotYourTurnException(SK8Exception):
    def __init__(self):
        super().__init__(
            detail="Not your turn to submit a clip",
            status_code=status.HTTP_403_FORBIDDEN
        )


class GPSValidationException(SK8Exception):
    def __init__(self, distance: float, max_distance: float):
        super().__init__(
            detail=f"GPS location too far from anchor: {distance:.2f} miles (max: {max_distance})",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class MatchNotFoundException(SK8Exception):
    def __init__(self, match_id: str = None):
        detail = f"Match {match_id} not found" if match_id else "Match not found"
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class UserNotFoundException(SK8Exception):
    def __init__(self, user_id: str = None):
        detail = f"User {user_id} not found" if user_id else "User not found"
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class InvalidCredentialsException(SK8Exception):
    def __init__(self):
        super().__init__(
            detail="Incorrect username or password",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class UserAlreadyExistsException(SK8Exception):
    def __init__(self, field: str):
        super().__init__(
            detail=f"{field.capitalize()} already registered",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class ClipTooLongException(SK8Exception):
    def __init__(self, duration: float, max_duration: int):
        super().__init__(
            detail=f"Clip duration {duration}s exceeds maximum {max_duration}s",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class ClipTooLargeException(SK8Exception):
    def __init__(self, size_mb: float, max_size_mb: int):
        super().__init__(
            detail=f"Clip size {size_mb:.1f}MB exceeds maximum {max_size_mb}MB",
            status_code=status.HTTP_400_BAD_REQUEST
        )
EOF

echo "✅ Created custom exceptions"

# Add validation helpers
cat > app/core/validators.py << 'EOF'
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
EOF

echo "✅ Created validators"

echo ""
echo "🎉 Error handling added!"
echo "Restart server to see changes"
