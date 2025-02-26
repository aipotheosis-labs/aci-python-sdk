from pydantic import BaseModel

from aipolabs.types.functions import Function


class SearchAppsParams(BaseModel):
    """Parameters for filtering applications.

    Parameters should be identical to the ones on the server side.

    """

    intent: str | None = None
    configured_only: bool = False
    categories: list[str] | None = None
    limit: int | None = None
    offset: int | None = None


class App(BaseModel):
    """Representation of an application. Search results will return a list of these."""

    # instance attributes should match the schema defined on the server side.
    name: str
    description: str


class AppDetails(App):
    """Detailed representation of an application, returned by App.get().
    Includes all base App fields plus functions supported by the app.
    """

    functions: list[Function]
