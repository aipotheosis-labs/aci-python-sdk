"""
This module defines the ACI_SEARCH_FUNCTIONS meta function, which can be used by LLMs/Agents to search for
relevant executable functions that can help complete tasks.

The ACI_SEARCH_FUNCTIONS is basically the json schema version of the SDK's client.functions.search(...) method,
but simplified with less parameters to make it more reliable for LLM function calling:
- It focuses primarily on the 'intent' parameter to find relevant functions
- It omits 'app_names', 'allowed_apps_only', 'format' parameters to simplify the interface
- It keeps pagination functionality with 'limit' and 'offset' parameters

Use this meta function when you want an LLM to discover relevant executable functions based on
the user's intent.
"""

from aci.meta_functions._base import MetaFunctionBase


class ACISearchFunctions(MetaFunctionBase):
    @classmethod
    def _get_base_schema(cls) -> dict:
        return {
            "name": "ACI_SEARCH_FUNCTIONS",
            "description": "This function allows you to find relevant executable functions and their schemas that can help complete your tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "intent": {
                        "type": "string",
                        "description": "Use this to find relevant functions you might need. Returned results of this "
                        "function will be sorted by relevance to the intent.",
                    },
                    "limit": {
                        "type": "integer",
                        "default": 100,
                        "description": "The maximum number of functions to return from the search per response.",
                        "minimum": 1,
                    },
                    "offset": {
                        "type": "integer",
                        "default": 0,
                        "minimum": 0,
                        "description": "Pagination offset.",
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
        }
