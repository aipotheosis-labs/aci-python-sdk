"""
This module defines the AIPOLABS_EXECUTE_FUNCTION meta function, which is used by LLM to submit
execution requests for indexed functions on aipolabs backend.

This module includes the schema definition for the function and a Pydantic model for
validating the execution parameters.
"""

from typing import Any

from pydantic import BaseModel

import aipolabs.meta_functions._aipolabs_get_function_definition as AipolabsGetFunctionDefinition

NAME = "AIPOLABS_EXECUTE_FUNCTION"
SCHEMA = {
    "type": "function",
    "function": {
        "name": NAME,
        "description": "Execute a specific retrieved function. Provide the executable function name, and the required function parameters for that function based on function definition retrieved.",
        "parameters": {
            "type": "object",
            "properties": {
                "function_name": {
                    "type": "string",
                    "description": f"The name of the function to execute, which is retrieved from the {AipolabsGetFunctionDefinition.NAME} function.",
                },
                "function_parameters": {
                    "type": "object",
                    "description": "This object contains the all input parameters in key-value pairs needed to execute the specified function. The required parameters depend on the 'function_name' and are provided in the function definition retrieved. For functions without parameters, provide an empty object",
                    "additionalProperties": True,
                },
            },
            "required": ["function_name", "function_parameters"],
            "additionalProperties": False,
        },
    },
}


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

    @classmethod
    def model_validate(cls, obj: dict, *args, **kwargs):  # type: ignore[no-untyped-def]
        # TODO: llm most time doesn't put input parameters in the function_parameters key when using AIPOLABS_EXECUTE_FUNCTION,
        # so we need to handle that here. It is a bit hacky, we should improve this in the future
        if "function_parameters" not in obj:
            # Create a copy of the input dict
            processed_obj = obj.copy()
            if "function_name" not in processed_obj:
                raise ValueError("function_name is required")
            # Extract function_name
            function_name = processed_obj.pop("function_name")
            # Create new dict with correct structure
            processed_obj = {
                "function_name": function_name,
                "function_parameters": processed_obj,  # All remaining fields go here
            }
            return super().model_validate(processed_obj, *args, **kwargs)
        return super().model_validate(obj, *args, **kwargs)


class FunctionExecutionResult(BaseModel):
    """Result of a Aipolabs indexed function (e.g. BRAVE_SEARCH__WEB_SEARCH) execution.
    Should be identical to the class defined on server side.
    """

    success: bool
    data: Any | None = None
    error: str | None = None


def validate_params(params: dict) -> FunctionExecutionParams:
    """Validate the parameters for executing a function.

    Returns:
        FunctionExecutionParams: The validated pydantic model instance.
    """
    return FunctionExecutionParams.model_validate(params)  # type: ignore[no-any-return]
