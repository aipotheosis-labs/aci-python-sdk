from pydantic import BaseModel


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

    Should match the schema defined on the server side.
    """

    name: str
    description: str
