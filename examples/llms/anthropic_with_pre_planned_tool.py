import os

import anthropic
from anthropic.types.content_block import TextBlock, ToolUseBlock
from dotenv import load_dotenv

from aipolabs._client import ACI
from aipolabs.types.functions import FunctionDefinitionFormat
from aipolabs.utils._logging import create_headline

load_dotenv()
LINKED_ACCOUNT_OWNER_ID = os.getenv("LINKED_ACCOUNT_OWNER_ID", "")
if not LINKED_ACCOUNT_OWNER_ID:
    raise ValueError("LINKED_ACCOUNT_OWNER_ID is not set")


def main() -> None:
    aci = ACI()
    github_get_user_function_definition = aci.functions.get_definition(
        "GITHUB__GET_USER", format=FunctionDefinitionFormat.ANTHROPIC
    )
    print(create_headline("Github get user function definition"))
    print(github_get_user_function_definition)

    client = anthropic.Anthropic()

    response = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=1000,
        temperature=1,
        system="You are a helpful assistant with access to a variety of tools.",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Tell me about the github user karpathy"}
                ],
            }
        ],
        tools=[github_get_user_function_definition],
    )

    for content_block in response.content:
        if isinstance(content_block, TextBlock):
            print(create_headline("LLM Response"))
            print(content_block.text)
        elif isinstance(content_block, ToolUseBlock):
            print(create_headline(f"Tool call: {content_block.name}"))
            print(f"arguments: {content_block.input}")

            result = aci.handle_function_call(
                content_block.name,
                content_block.input,
                linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
                format=FunctionDefinitionFormat.ANTHROPIC,
            )

            print(f"{create_headline('Function Call Result')} \n {result}")


if __name__ == "__main__":
    main()
