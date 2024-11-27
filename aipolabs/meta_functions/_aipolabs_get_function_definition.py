"""
This module defines the AIPOLABS_GET_FUNCTION_DEFINITION meta function, which is used by LLM to retrieve
the definition of an executable function.

The function requires one key parameter:
1. function_name: The name of the function to get the definition for. e.g. `BRAVE_SEARCH__WEB_SEARCH`

It returns json schema of the function definition.
"""

from pydantic import BaseModel

NAME = "AIPOLABS_GET_FUNCTION_DEFINITION"

SCHEMA = {
    "type": "function",
    "function": {
        "name": NAME,
        "description": "This function allows you to get the definition of an executable function.",
        "parameters": {
            "type": "object",
            "properties": {
                "function_name": {
                    "type": "string",
                    "description": "The name of the function you want to get the definition for. You can get function names by using the AIPOLABS_SEARCH_FUNCTIONS function.",
                }
            },
            "required": ["function_name"],
            "additionalProperties": False,
        },
    },
}


class GetFunctionDefinitionParams(BaseModel):
    """Parameters for getting a function definition.

    The backend require "inference_provider" parameter but this value should be set by developer not LLM when using the sdk.
    """

    function_name: str


def validate_params(params: dict) -> GetFunctionDefinitionParams:
    validated_params: GetFunctionDefinitionParams = GetFunctionDefinitionParams.model_validate(
        params
    )
    return validated_params
