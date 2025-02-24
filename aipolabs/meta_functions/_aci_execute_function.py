"""
This module defines the ACI_EXECUTE_FUNCTION meta function, which is used by LLM to submit
execution requests for indexed functions on aipolabs ACI backend.

This module includes the schema definition for the function and a Pydantic model for
validating the execution parameters.
"""

import aipolabs.meta_functions._aci_get_function_definition as ACIGetFunctionDefinition

NAME = "ACI_EXECUTE_FUNCTION"
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
                    "description": f"The name of the function to execute, which is retrieved from the {ACIGetFunctionDefinition.NAME} function.",
                },
                "function_arguments": {
                    "type": "object",
                    "description": "A dictionary containing key-value pairs of input parameters required by the specified function. The parameter names and types must match those defined in the function definition previously retrieved. If the function requires no parameters, provide an empty object.",
                    "additionalProperties": True,
                },
            },
            "required": ["function_name", "function_arguments"],
            "additionalProperties": False,
        },
    },
}


def wrap_function_arguments_if_not_present(obj: dict) -> dict:
    if "function_arguments" not in obj:
        # Create a copy of the input dict
        processed_obj = obj.copy()
        if "function_name" not in processed_obj:
            raise ValueError("function_name is required")
        # Extract function_name
        function_name = processed_obj.pop("function_name")
        # Create new dict with correct structure
        processed_obj = {
            "function_name": function_name,
            "function_arguments": processed_obj,  # All remaining fields go here
        }
        return processed_obj
    return obj
