class AipolabsError(Exception):
    """Base exception for all Aipolabs SDK errors"""

    def __init__(self, message: str):
        super().__init__(message)


class APIKeyNotFound(AipolabsError):
    """Raised when the API key is not found."""

    pass


class AuthenticationError(AipolabsError):
    """Raised when there are authentication issues (401)"""

    pass


class PermissionError(AipolabsError):
    """Raised when the user doesn't have permission (403)"""

    pass


class NotFoundError(AipolabsError):
    """Raised when the requested resource is not found (404)"""

    pass


class ValidationError(AipolabsError):
    """Raised when the request is invalid (400)"""

    pass


class RateLimitError(AipolabsError):
    """Raised when rate limit is exceeded (429)"""

    pass


class ServerError(AipolabsError):
    """Raised when server errors occur (500-series)"""

    pass


class UnknownError(AipolabsError):
    """Raised when an unknown error occurs"""

    pass


class MissingLinkedAccountOwnerId(AipolabsError):
    """Raised when linked_account_owner_id is missing for function execution"""

    def __init__(self) -> None:
        super().__init__(
            "linked_account_owner_id is required for function execution, "
            "please provide it to the 'Aipolabs' client constructor or override it in the 'handle_function_call' method"
        )
