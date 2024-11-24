from pydantic import BaseModel

AIPOLABS_GET_FUNCTION_DEFINITION_NAME = "AIPOLABS_GET_FUNCTION_DEFINITION"

AIPOLABS_GET_FUNCTION_DEFINITION = {
    "type": "function",
    "function": {
        "name": AIPOLABS_GET_FUNCTION_DEFINITION_NAME,
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
