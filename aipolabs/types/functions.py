from typing import Any, ClassVar

from pydantic import BaseModel


class GetFunctionDefinitionParams(BaseModel):
    """Parameters for getting a function definition.

    The backend require "inference_provider" parameter but this value should be set by
    developer not LLM when using the sdk, so inference_provider parameter is not present in SCHEMA above.
    """

    function_name: str
    inference_provider: str | None


class FunctionExecutionParams(BaseModel):
    """Parameters for executing a function.

    The function requires two key parameters:
    1. function_name: The name of the function to execute, which is the function name of the function that is
    retrieved using the AIPOLABS_GET_FUNCTION_DEFINITION meta function.
    2. function_parameters: A dictionary containing all input parameters required to execute
    the specified function. These parameters are also provided by the function definition
    retrieved using the AIPOLABS_GET_FUNCTION_DEFINITION meta function. If a function does not require parameters, an empty dictionary should be provided.
    """

    function_name: str
    function_parameters: dict


class FunctionExecutionResult(BaseModel):
    """Result of a Aipolabs indexed function (e.g. BRAVE_SEARCH__WEB_SEARCH) execution.
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
    limit: int | None = None
    offset: int | None = None


class Function(BaseModel):
    """Representation of a function. Search results will return a list of these.
    Also provides enum-like functionality for supported functions.

    Each function is associated with a specific application. The prefix of the function name
    is actually the application name. For example, the function name
    `BRAVE_SEARCH__WEB_SEARCH` is a function that belongs to the `BRAVE_SEARCH` application.

    The function name uniquely identifies a function.

    Please note that we might add new Functions in our backend dynamically, so the constant values might
    not be exhaustive. You can either upgrade your SDK to the latest version or just use string values
    (e.g. "BRAVE_SEARCH__WEB_SEARCH", check out docs for most up-to-date list of supported functions)
    for Function related operations.
    """

    name: str
    description: str

    # Class-level constants for supported functions
    BRAVE_SEARCH__WEB_SEARCH: ClassVar[str] = "BRAVE_SEARCH__WEB_SEARCH"
