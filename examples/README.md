# Example agent loops with the Aipolabs Python SDK

This directory contains example implementations demonstrating different approaches to using the Aipolabs Python SDK with LLM agents.

## Examples

### 1. Agent with Pre-planned Functions

[agent_with_pre_planned_functions.py](./agent_with_pre_planned_functions.py)

This example demonstrates the simplest way to use Aipolabs functions with an LLM agent. It:
- Pre-selects specific functions by developers before the conversation


### 2. Agent with Dynamic Function Discovery and Fixed Tools

[agent_with_dynamic_function_discovery_and_fixed_tools.py](./agent_with_dynamic_function_discovery_and_fixed_tools.py)

- Use all 4 meta functions (AIPOLABS_SEARCH_APPS, AIPOLABS_SEARCH_FUNCTIONS, AIPOLABS_GET_FUNCTION_DEFINITION, AIPOLABS_EXECUTE_FUNCTION)


### 3. Agent with Dynamic Function Discovery and Dynamic Tools

[agent_with_dynamic_function_discovery_and_dynamic_tools.py](./agent_with_dynamic_function_discovery_and_dynamic_tools.py)

- Use 3 meta functions (AIPOLABS_SEARCH_APPS, AIPOLABS_SEARCH_FUNCTIONS, AIPOLABS_GET_FUNCTION_DEFINITION)



## Key Differences Between example 2 and 3

- In example 2, the retrieved function definition (e.g., `BRAVE_SEARCH__WEB_SEARCH`) is fed directly to the LLM as chat text, and the LLM generates parameters based on the function definition and then generates a `AIPOLABS_EXECUTE_FUNCTION` function call.

- In example 3, the retrieved function definition is stored in the `tools_retrieved` list, and can be dynamically appended to or removed from the LLM's tool list. The LLM will generate a direct function call that matches the retrieved function. (e.g., `BRAVE_SEARCH__WEB_SEARCH`)


## Running the examples
The examples are runnable, for a quick setup:
- Clone the whole repository and install dependencies `poetry install`
- Set your OpenAI API key (set as `OPENAI_API_KEY` in your environment)
- Set your Aipolabs API key (set as `AIPOLABS_API_KEY` in your environment)
- Change the `linked_account_owner_id` in the `handle_function_call` method to your own account owner id (need to be linked in the Aipolabs dev portal first)
- Run any example: `poetry run python examples/agent_with_pre_planned_functions.py`