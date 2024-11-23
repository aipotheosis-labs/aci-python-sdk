"""
Optionally you can provide AIPOLABS_EXECUTE_FUNCTION as one of the tools to the LLM.
This is an alternative approach to appending the fetched function definition to the tools list.
"""

from pydantic import BaseModel

from aipolabs.tools.fetch_function_definition import (
    AIPOLABS_FETCH_FUNCTION_DEFINITION_NAME,
)

AIPOLABS_EXECUTE_FUNCTION_NAME = "AIPOLABS_EXECUTE_FUNCTION"
AIPOLABS_EXECUTE_FUNCTION = {
    "type": "function",
    "function": {
        "name": AIPOLABS_EXECUTE_FUNCTION_NAME,
        "description": "Execute a specific fetched function. Provide the executable function name, and the required function parameters for that function based on function definition fetched.",
        "parameters": {
            "type": "object",
            "properties": {
                "function_name": {
                    "type": "string",
                    "description": f"The name of the function to execute, as provided in the content retrieved from the {AIPOLABS_FETCH_FUNCTION_DEFINITION_NAME} function.",
                },
                "function_parameters": {
                    "type": "object",
                    "description": "This object contains the all input parameters in key-value pairs needed to execute the specified function. The required parameters depend on the 'function_name' and are provided in the function definition fetched. For functions without parameters, provide an empty object",
                    "additionalProperties": True,
                },
            },
            "required": ["function_name", "function_parameters"],
            "additionalProperties": False,
        },
    },
}


class ExecuteFunctionParameters(BaseModel):
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
