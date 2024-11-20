class AipolabsError(Exception):
    """Base class for all Aipolabs exceptions."""


class APIKeyNotFound(AipolabsError):
    """Raised when the API key is not found."""
