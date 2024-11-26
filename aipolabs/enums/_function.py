from enum import Enum


class Function(str, Enum):
    """Enumeration of supported functions indexed by the backend server.

    This enum class defines the list of executable functions that are currently
    supported and indexed by our backend server. Each function is associated with
    a specific application. So the prefix of the function name is actually the
    application name. For example, the function name
    `BRAVE_SEARCH__WEB_SEARCH` is a function that belongs to the
    `BRAVE_SEARCH` application.

    The function name uniquely identifies a function.
    """

    BRAVE_SEARCH__WEB_SEARCH = "BRAVE_SEARCH__WEB_SEARCH"
