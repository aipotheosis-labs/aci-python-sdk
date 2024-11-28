"""
This module defines the AIPOLABS_EXECUTE_FUNCTION meta function, which is used by LLM to submit
execution requests for indexed functions on aipolabs backend.

This module includes the schema definition for the function and a Pydantic model for
validating the execution parameters.
"""

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


def wrap_function_parameters_if_not_present(obj: dict) -> dict:
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
        return processed_obj
    return obj
