import json

from dotenv import load_dotenv
from openai import OpenAI

from aipolabs import (
    AIPOLABS_EXECUTE_FUNCTION,
    AIPOLABS_FETCH_FUNCTION_DEFINITION,
    AIPOLABS_SEARCH_APPS,
    AIPOLABS_SEARCH_FUNCTIONS,
    Aipolabs,
)
from aipolabs.utils.logging import create_headline

load_dotenv()

# gets OPENAI_API_KEY from your environment variables
openai = OpenAI()
# gets AIPOLABS_API_KEY from your environment variables
aipolabs = Aipolabs()

prompt = (
    "You are a helpful assistant with access to a unlimited number of tools via four meta functions: "
    "AIPOLABS_SEARCH_APPS, AIPOLABS_SEARCH_FUNCTIONS, AIPOLABS_FETCH_FUNCTION_DEFINITION, and AIPOLABS_EXECUTE_FUNCTION."
    "You can use AIPOLABS_SEARCH_APPS to find relevant apps (which include a set of functions), if you find Apps that might help with your tasks you can use AIPOLABS_SEARCH_FUNCTIONS to find relevant functions within certain apps."
    "You can also use AIPOLABS_SEARCH_FUNCTIONS directly to find relevant functions across all apps."
    "Once you have identified the function you need to use, you can use AIPOLABS_FETCH_FUNCTION_DEFINITION to fetch the definition of the function."
    "You can then use AIPOLABS_EXECUTE_FUNCTION to execute the function provided you have the correct parameters."
)

# aipolabs meta functions for the LLM to discover the available executale functions dynamically
tools_meta = [
    AIPOLABS_SEARCH_APPS,
    AIPOLABS_SEARCH_FUNCTIONS,
    AIPOLABS_FETCH_FUNCTION_DEFINITION,
    AIPOLABS_EXECUTE_FUNCTION,
]


def main() -> None:
    # Start the LLM processing loop
    chat_history: list[dict] = []

    while True:
        print(create_headline("Waiting for LLM Output"))
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                },
                {
                    "role": "user",
                    "content": "get me some online information about aipolabs",
                },
            ]
            + chat_history,
            tools=tools_meta,
            # tool_choice="required",  # force the model to generate a tool call
            parallel_tool_calls=False,
        )

        # Process LLM response and potential function call (there can only be at most one function call)
        content = response.choices[0].message.content
        tool_call = (
            response.choices[0].message.tool_calls[0]
            if response.choices[0].message.tool_calls
            else None
        )
        if content:
            print(f"{create_headline('LLM Message')} \n {content}")
            chat_history.append({"role": "assistant", "content": content})

        # Handle function call if any
        if tool_call:
            print(
                f"{create_headline(f'Function Call: {tool_call.function.name}')} \n arguments: {tool_call.function.arguments}"
            )

            chat_history.append({"role": "assistant", "tool_calls": [tool_call]})
            function_call_type, result = aipolabs.handle_function_call(
                tool_call.function.name, json.loads(tool_call.function.arguments)
            )

            print(f"{create_headline('Function Call Result')} \n {result}")
            # Continue loop, feeding the result back to the LLM for further instructions
            chat_history.append(
                {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)}
            )
        else:
            # If there's no further function call, exit the loop
            print(create_headline("Task Completed"))
            break


if __name__ == "__main__":
    main()
