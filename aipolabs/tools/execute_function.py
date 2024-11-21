# There should not be a AIPOLABS_EXECUTE_FUNCTION function definition provided to the LLM as one of the tools.
# Instead, we should provide the LLM with the function definition it fetched using the AIPOLABS_FETCH_FUNCTION_DEFINITION function.
# And have the LLM make function call direclty based on that fetched function definition.
