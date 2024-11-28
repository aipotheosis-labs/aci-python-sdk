"""
This module defines the AIPOLABS_SEARCH_APPS meta function, which is used by LLM to search for
relevant applications (which include a set of functions) that can help complete a task.
"""

from pydantic import BaseModel

NAME = "AIPOLABS_SEARCH_APPS"

SCHEMA = {
    "type": "function",
    "function": {
        "name": NAME,
        "description": "This function allows you to find relevant apps (which includeds a set of functions) that can help complete your tasks or get data and information you need.",
        "parameters": {
            "type": "object",
            "properties": {
                "intent": {
                    "type": ["string", "null"],
                    "description": "Use this to find relevant apps you might need. Returned results of this function will be sorted by relevance to the intent. Examples include 'what's the top news in the stock market today', 'i want to automate outbound marketing emails'.",
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
            "required": ["intent", "limit", "offset"],
            "additionalProperties": False,
        },
    },
}


class SearchAppsParams(BaseModel):
    """Parameters for filtering applications.

    Parameters should be identical to the ones on the server side.

    TODO: Add categories field.
    """

    intent: str | None = None
    limit: int | None = None
    offset: int | None = None


class App(BaseModel):
    """Representation of an application. Search results will return a list of these.

    Should match the schema defined on the server side.
    """

    name: str
    description: str
