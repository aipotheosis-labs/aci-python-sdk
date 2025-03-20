import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from aipolabs import ACI
from aipolabs.types.functions import FunctionDefinitionFormat
from aipolabs.utils._logging import create_headline

load_dotenv()
LINKED_ACCOUNT_OWNER_ID = os.getenv("LINKED_ACCOUNT_OWNER_ID", "")
if not LINKED_ACCOUNT_OWNER_ID:
    raise ValueError("LINKED_ACCOUNT_OWNER_ID is not set")

# gets OPENAI_API_KEY from your environment variables
openai = OpenAI()
# gets AIPOLABS_ACI_API_KEY from your environment variables
aci = ACI()


def main() -> None:
    # For a list of all supported apps and functions, please go to the platform.aci.dev
    brave_search_function_definition = aci.functions.get_definition("BRAVE_SEARCH__WEB_SEARCH")

    print(create_headline("Brave search function definition"))
    print(brave_search_function_definition)

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant with access to a variety of tools.",
            },
            {
                "role": "user",
                "content": "What is aipolabs ACI?",
            },
        ],
        tools=[brave_search_function_definition],
        tool_choice="required",  # force the model to generate a tool call for demo purposes
    )
    tool_call = (
        response.choices[0].message.tool_calls[0]
        if response.choices[0].message.tool_calls
        else None
    )

    if tool_call:
        print(create_headline(f"Tool call: {tool_call.function.name}"))
        print(f"arguments: {tool_call.function.arguments}")
        # submit the selected function and its arguments to aipolabs ACI backend for execution
        result = aci.handle_function_call(
            tool_call.function.name,
            json.loads(tool_call.function.arguments),
            linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
            allowed_apps_only=True,
            format=FunctionDefinitionFormat.OPENAI,
        )
        """
        alternatively, because this is a direct function execution you can use the following:
        result = aci.functions.execute(
            tool_call.function.name,
            json.loads(tool_call.function.arguments),
            linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
        )
        """
        print(f"{create_headline('Function Call Result')} \n {result}")


if __name__ == "__main__":
    main()
