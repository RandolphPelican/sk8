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
