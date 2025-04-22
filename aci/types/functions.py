from typing import Any

from pydantic import BaseModel

from aci.types.enums import FunctionDefinitionFormat


class GetFunctionDefinitionParams(BaseModel):
    """Parameters for getting a function definition.

    The backend requires "format" parameter but this value should be set by the
    developer and not LLM when using the sdk, so the 'format' parameter is not present in meta SCHEMA.
    """

    function_name: str
    format: FunctionDefinitionFormat


class FunctionExecutionParams(BaseModel):
    """Parameters for executing a function.

    The function requires two key parameters:
    1. function_name: The name of the function to execute (e.g. "BRAVE_SEARCH__WEB_SEARCH")
    2. function_arguments: A dictionary containing all input arguments required to execute
    the specified function. If the function requires no arguments, an empty dictionary should be provided.
    3. linked_account_owner_id: to specify with credentials of which linked account the
    function should be executed.
    """

    function_name: str
    function_arguments: dict
    linked_account_owner_id: str


class FunctionExecutionResult(BaseModel):
    """Result of a ACI indexed function (tools) (e.g. "BRAVE_SEARCH__WEB_SEARCH") execution.
    Should be identical to the class defined on server side.
    """

    success: bool
    data: Any | None = None
    error: str | None = None


class SearchFunctionsParams(BaseModel):
    """Parameters for searching functions.

    Parameters should be identical to the ones on the server side.
    """

    app_names: list[str] | None = None
    intent: str | None = None
    allowed_apps_only: bool = False
    format: FunctionDefinitionFormat = FunctionDefinitionFormat.OPENAI
    limit: int | None = None
    offset: int | None = None


class Function(BaseModel):
    name: str
    description: str


class FunctionDetails(BaseModel):
    id: str
    app_name: str
    name: str
    description: str
    tags: list[str]
    visibility: str
    active: bool
    protocol: str
    protocol_data: dict
    parameters: dict
    response: dict
