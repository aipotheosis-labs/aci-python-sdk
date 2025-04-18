"""
This module defines the ACI_SEARCH_FUNCTIONS_WITH_INTENT meta function, which is used by LLM to search for
relevant executable functions that can help complete a task.

This function is similar to ACI_SEARCH_FUNCTIONS, but it removes the app_names parameter for a
simplified workflow (Otherwise you'd have to call ACI_SEARCH_APPS first to get the app names).
"""

NAME = "ACI_SEARCH_FUNCTIONS_WITH_INTENT"
SCHEMA = {
    "type": "function",
    "function": {
        "name": NAME,
        "description": "This function allows you to find relevant executable functions (tools) that can help "
        "complete your tasks or get data and information you need.",
        "parameters": {
            "type": "object",
            "properties": {
                "intent": {
                    "type": "string",
                    "description": "Use this to discover relevant functions (tools) you might need. Returned "
                    "results of this function will be sorted by relevance to the intent. Examples "
                    "include 'what's the top news in the stock market today', 'i want to "
                    "automate outbound marketing emails'.",
                },
                "limit": {
                    "type": "integer",
                    "default": 100,
                    "description": "The maximum number of functions to return from the search per response.",
                    "minimum": 1,
                    "maximum": 1000,
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
    },
}
