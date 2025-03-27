import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from aipolabs import ACI
from aipolabs.types.functions import FunctionDefinitionFormat
from aipolabs.utils._logging import create_headline

load_dotenv()
LINKED_ACCOUNT_OWNER_ID = os.getenv("LINKED_ACCOUNT_OWNER_ID", "")
if not LINKED_ACCOUNT_OWNER_ID:
    raise ValueError("LINKED_ACCOUNT_OWNER_ID is not set")


def main() -> None:
    aci = ACI()
    github_get_user_function_definition = aci.functions.get_definition(
        "GITHUB__GET_USER"
    )
    print(create_headline("Github get user function definition"))
    print(github_get_user_function_definition)

    llm = ChatOpenAI(model="gpt-4o-mini")
    llm_with_tools = llm.bind_tools([github_get_user_function_definition])
    response = llm_with_tools.invoke("Tell me about the github user karpathy")

    tool_call = response.tool_calls[0] if response.tool_calls else None

    if tool_call:
        print(create_headline(f"Tool call: {tool_call['name']}"))
        print(f"arguments: {tool_call['args']}")

        result = aci.handle_function_call(
            tool_call["name"],
            tool_call["args"],
            linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
            format=FunctionDefinitionFormat.OPENAI,
        )

        print(f"{create_headline('Function Call Result')} \n {result}")


if __name__ == "__main__":
    main()
