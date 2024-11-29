from typing import ClassVar

from pydantic import BaseModel

from aipolabs.types.functions import Function


class SearchAppsParams(BaseModel):
    """Parameters for filtering applications.

    Parameters should be identical to the ones on the server side.

    TODO: Add categories field.
    """

    intent: str | None = None
    limit: int | None = None
    offset: int | None = None


class App(BaseModel):
    """Representation of an application. Search results will return a list of these.
    Also provides enum-like functionality for easily accessing supported applications.

    Please note that we might add new Apps in our backend dynamically, so the constant values might
    not be exhaustive.
    You can either upgrade your SDK to the latest version or just use string values
    (e.g. "BRAVE_SEARCH__WEB_SEARCH", check out docs for most up-to-date list of supported apps)
    for App related operations.
    """

    # instance attributes should match the schema defined on the server side.
    name: str
    description: str

    # Class-level constants for supported apps
    BRAVE_SEARCH__WEB_SEARCH: ClassVar[str] = "BRAVE_SEARCH__WEB_SEARCH"


class AppDetails(App):
    """Detailed representation of an application, returned by App.get().
    Includes all base App fields plus functions supported by the app.
    """

    functions: list[Function]
