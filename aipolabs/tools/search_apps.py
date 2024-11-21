from pydantic import BaseModel

AIPOLABS_SEARCH_APPS = {
    "type": "function",
    "function": {
        "name": "AIPOLABS_SEARCH_APPS",
        "strict": True,
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


class SearchAppsParameters(BaseModel):
    intent: str | None = None
    limit: int | None = None
    offset: int | None = None
