AIPOLABS_FETCH_FUNCTION_DEFINITION = {
    "type": "function",
    "function": {
        "name": "AIPOLABS_FETCH_FUNCTION_DEFINITION",
        "strict": True,
        "description": "This function allows you to fetch the definition of an executable function.",
        "parameters": {
            "type": "object",
            "properties": {
                "function_name": {
                    "type": "string",
                    "description": "The name of the function you want to fetch the definition for. You can get function names by using the AIPOLABS_SEARCH_FUNCTIONS function.",
                }
            },
            "required": ["function_name"],
            "additionalProperties": False,
        },
    },
}
