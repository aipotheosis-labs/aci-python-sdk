from enum import Enum


class App(str, Enum):
    """Enumeration of supported applications indexed by the backend server.

    This enum class defines the list of applications that are currently supported
    and indexed by our backend server, of which the functions can be executed.

    The app name uniquely identifies an application.
    """

    BRAVE_SEARCH = "BRAVE_SEARCH"
