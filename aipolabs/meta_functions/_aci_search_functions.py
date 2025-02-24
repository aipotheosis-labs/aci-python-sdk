"""
This module defines the ACI_SEARCH_FUNCTIONS meta function, which is used by LLM to search for
relevant executable functions that can help complete a task.

You can filter by adding app names, which can be retrieved using the ACI_SEARCH_APPS meta function.
"""

NAME = "ACI_SEARCH_FUNCTIONS"
SCHEMA = {
    "type": "function",
    "function": {
        "name": NAME,
        "description": "This function allows you to find relevant executable functions that can help complete your tasks or get data and information you need.",
        "parameters": {
            "type": "object",
            "properties": {
                "app_names": {
                    "type": ["array", "null"],
                    "items": {"type": "string"},
                    "default": "null",
                    "description": "The names of the apps you want to search functions for If provided, the search will be limited to the functions of the specified apps. Use null to search functions across all apps. You can find app names by first using the ACI_SEARCH_APPS function.",
                },
                "intent": {
                    "type": ["string", "null"],
                    "description": "Use this to find relevant functions you might need. Returned results of this function will be sorted by relevance to the intent. Examples include 'what's the top news in the stock market today', 'i want to automate outbound marketing emails'.",
                },
                "limit": {
                    "type": ["integer", "null"],
                    "default": 100,
                    "description": "The maximum number of apps to return from the search.",
                    "minimum": 1,
                    "maximum": 1000,
                },
                "offset": {
                    "type": ["integer", "null"],
                    "default": 0,
                    "minimum": 0,
                    "description": "Pagination offset.",
                },
            },
            "required": ["app_names", "intent", "limit", "offset"],
            "additionalProperties": False,
        },
    },
}
