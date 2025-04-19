class ACIError(Exception):
    """Base exception for all ACI SDK errors"""

    def __init__(self, message: str):
        super().__init__(message)


class APIKeyNotFound(ACIError):
    """Raised when the API key is not found."""

    pass


class AuthenticationError(ACIError):
    """Raised when there are authentication issues (401)"""

    pass


class PermissionError(ACIError):
    """Raised when the user doesn't have permission (403)"""

    pass


class NotFoundError(ACIError):
    """Raised when the requested resource is not found (404)"""

    pass


class ValidationError(ACIError):
    """Raised when the request is invalid (400)"""

    pass


class RateLimitError(ACIError):
    """Raised when rate limit is exceeded (429)"""

    pass


class ServerError(ACIError):
    """Raised when server errors occur (500-series)"""

    pass


class UnknownError(ACIError):
    """Raised when an unknown error occurs"""

    pass
