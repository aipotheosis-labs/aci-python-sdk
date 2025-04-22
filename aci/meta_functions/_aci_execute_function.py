"""
This module defines the ACI_EXECUTE_FUNCTION meta function, which can be used by LLMs to send
execution requests for functions discovered and selected through the ACISearchFunctions.

The ACI_EXECUTE_FUNCTION is the json schema version of the SDK's client.functions.execute(...) method,
adapted for LLM function calling:
- It requires 'function_name' to specify which function to execute
- It requires 'function_arguments' containing parameters needed by the target function
- The 'linked_account_owner_id' parameter is removed here to avoid LLM hallucination. It should be passed directly to client.handle_function_call(...)

This is typically the final step in the dynamic function discovery and execution flow:
1. Use ACI_SEARCH_FUNCTIONS to find relevant functions
2. Use ACI_EXECUTE_FUNCTION to actually execute the chosen function with the proper arguments

Note: The module contains a helper function that fixes cases where LLMs might incorrectly
format function arguments, ensuring more reliable execution.
"""

from aci.meta_functions._base import MetaFunctionBase


class ACIExecuteFunction(MetaFunctionBase):
    @classmethod
    def _get_base_schema(cls) -> dict:
        return {
            "name": "ACI_EXECUTE_FUNCTION",
            "description": "Execute a specific retrieved function. Provide the executable function name, and the "
            "required function parameters for that function based on function definition retrieved.",
            "parameters": {
                "type": "object",
                "properties": {
                    "function_name": {
                        "type": "string",
                        "description": "The name of the function to execute",
                    },
                    "function_arguments": {
                        "type": "object",
                        "description": "A dictionary containing key-value pairs of input parameters required by the "
                        "specified function. The parameter names and types must match those defined in "
                        "the function definition previously retrieved. If the function requires no "
                        "parameters, provide an empty object.",
                        "additionalProperties": True,
                    },
                },
                "required": ["function_name", "function_arguments"],
                "additionalProperties": False,
            },
        }

    @classmethod
    def wrap_function_arguments_if_not_present(cls, obj: dict) -> dict:
        """
        This is a hacky fix in case some (and sometimes) LLM outputs the function arguments without the function_arguments key.
        """
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
