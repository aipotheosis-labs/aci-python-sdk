import json
import os

from crewai import Agent, Task
from crewai.tools import tool
from dotenv import load_dotenv

from aipolabs._client import ACI
from aipolabs.types.functions import FunctionDefinitionFormat

load_dotenv()
LINKED_ACCOUNT_OWNER_ID = os.getenv("LINKED_ACCOUNT_OWNER_ID", "")
if not LINKED_ACCOUNT_OWNER_ID:
    raise ValueError("LINKED_ACCOUNT_OWNER_ID is not set")


@tool
def github_get_user(username: str) -> str:
    """Get github user information"""
    aci = ACI()

    result = aci.handle_function_call(
        "GITHUB__GET_USER",
        {"path": {"username": username}},
        linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
        format=FunctionDefinitionFormat.ANTHROPIC,
    )
    return json.dumps(result)


def main() -> None:
    agent = Agent(
        role="Assistant",
        backstory="You are a helpful assistant that can use available tools to help the user.",
        goal="Help with user requests",
        tools=[github_get_user],
        function_calling_llm="gpt-4o-mini",
        verbose=True,
    )

    task = Task(
        description="Tell me about the github user karpathy",
        expected_output="A description of the github user karpathy",
    )

    response = agent.execute_task(task)
    print(response)


if __name__ == "__main__":
    main()
