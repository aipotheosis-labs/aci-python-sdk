from pydantic import BaseModel

from aci.types.functions import Function, FunctionDetails


class SearchAppsParams(BaseModel):
    """Parameters for filtering applications.

    Parameters should be identical to the ones on the server side.

    """

    intent: str | None = None
    allowed_apps_only: bool = False
    include_functions: bool = False
    categories: list[str] | None = None
    limit: int | None = None
    offset: int | None = None


class AppBasic(BaseModel):
    """Representation of an application. Search results will return a list of these."""

    # instance attributes should match the schema defined on the server side.
    name: str
    description: str
    functions: list[Function] | None = None


class AppDetails(BaseModel):
    """Detailed representation of an application, returned by App.get()."""

    id: str
    name: str
    display_name: str
    provider: str
    version: str
    description: str
    logo: str | None
    categories: list[str]
    visibility: str
    active: bool
    security_schemes: list[str]
    functions: list[FunctionDetails]
