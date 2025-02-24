class AipolabsACIError(Exception):
    """Base exception for all Aipolabs SDK errors"""

    def __init__(self, message: str):
        super().__init__(message)


class APIKeyNotFound(AipolabsACIError):
    """Raised when the API key is not found."""

    pass


class AuthenticationError(AipolabsACIError):
    """Raised when there are authentication issues (401)"""

    pass


class PermissionError(AipolabsACIError):
    """Raised when the user doesn't have permission (403)"""

    pass


class NotFoundError(AipolabsACIError):
    """Raised when the requested resource is not found (404)"""

    pass


class ValidationError(AipolabsACIError):
    """Raised when the request is invalid (400)"""

    pass


class RateLimitError(AipolabsACIError):
    """Raised when rate limit is exceeded (429)"""

    pass


class ServerError(AipolabsACIError):
    """Raised when server errors occur (500-series)"""

    pass


class UnknownError(AipolabsACIError):
    """Raised when an unknown error occurs"""

    pass
