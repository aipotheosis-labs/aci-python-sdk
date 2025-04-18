from enum import Enum


class SecurityScheme(str, Enum):
    """
    security scheme type for an app
    """

    NO_AUTH = "no_auth"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"


class Visibility(str, Enum):
    """Visibility of an app or function."""

    PUBLIC = "public"
    PRIVATE = "private"
