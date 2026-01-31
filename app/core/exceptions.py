"""Custom exceptions for the application."""

from typing import Any, Dict, Optional


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(AppException):
    """Authentication failed."""

    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=401, details=details)


class AuthorizationError(AppException):
    """Authorization failed - insufficient permissions."""

    def __init__(self, message: str = "Insufficient permissions", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, details=details)


class NotFoundError(AppException):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, details=details)


class ValidationError(AppException):
    """Validation error."""

    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, details=details)


class ConflictError(AppException):
    """Resource conflict (e.g., duplicate)."""

    def __init__(self, message: str = "Resource conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=409, details=details)


class RateLimitError(AppException):
    """Rate limit exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=429, details=details)


class MFARequiredError(AppException):
    """MFA verification required."""

    def __init__(self, message: str = "MFA verification required", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, details=details)


class AccountLockedError(AppException):
    """Account is locked due to failed login attempts."""

    def __init__(self, message: str = "Account locked", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, details=details)


class ConcurrentModificationError(AppException):
    """Concurrent modification detected (optimistic locking)."""

    def __init__(self, message: str = "Resource was modified by another request", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=409, details=details)
