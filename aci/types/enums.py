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


class FunctionDefinitionFormat(str, Enum):
    BASIC = "basic"  # name and description only
    OPENAI = "openai"  # openai function call format (for the chat completions api)
    OPENAI_RESPONSES = (
        "openai_responses"  # openai function call format (for the responses api, the newest API)
    )
    ANTHROPIC = "anthropic"  # anthropic function call format
