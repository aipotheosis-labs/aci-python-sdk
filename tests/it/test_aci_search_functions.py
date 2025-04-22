import json
import os
from typing import Any

import pytest
from openai import OpenAI

from aci import ACI
from aci.meta_functions import ACIExecuteFunction, ACISearchFunctions
from aci.types.enums import FunctionDefinitionFormat

ACI_API_KEY = os.getenv("ACI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# TODO: fix type ignores
@pytest.mark.skipif(ACI_API_KEY is None, reason="ACI_API_KEY is not set")
@pytest.mark.skipif(OPENAI_API_KEY is None, reason="OPENAI_API_KEY is not set")
def test_aci_search_functions() -> None:
    aci = ACI(api_key=ACI_API_KEY)
    openai = OpenAI(api_key=OPENAI_API_KEY)

    # search for functions
    aci_search_functions = ACISearchFunctions.to_json_schema(
        FunctionDefinitionFormat.OPENAI_RESPONSES
    )
    aci_execute_function = ACIExecuteFunction.to_json_schema(
        FunctionDefinitionFormat.OPENAI_RESPONSES
    )

    # trigger search function call
    input_messages: list[Any] = [
        {"role": "user", "content": "Can you star aipotheosis-labs/aci github repo?"}
    ]
    openai_response = openai.responses.create(
        model="gpt-4o",
        input=input_messages,
        tools=[aci_search_functions, aci_execute_function],  # type: ignore
    )
    assert openai_response.output[0].name == ACISearchFunctions.get_name()  # type: ignore
    input_messages.append(openai_response.output[0])

    # handle search function call
    aci_response = aci.handle_function_call(
        openai_response.output[0].name,  # type: ignore
        json.loads(openai_response.output[0].arguments),  # type: ignore
        linked_account_owner_id="<owner_id doesn't matter for search functions call>",
        format=FunctionDefinitionFormat.OPENAI_RESPONSES,
    )
    assert len(aci_response) > 0
    assert aci_response[0]["name"] == "GITHUB__STAR_REPOSITORY"

    input_messages.append(
        {
            "type": "function_call_output",
            "call_id": openai_response.output[0].call_id,  # type: ignore
            "output": str(aci_response),
        }
    )

    # trigger execute function call
    openai_response = openai.responses.create(
        model="gpt-4o",
        input=input_messages,
        tools=[aci_search_functions, aci_execute_function],  # type: ignore
    )

    assert openai_response.output[0].name == ACIExecuteFunction.get_name()  # type: ignore
    generated_arguments = json.loads(openai_response.output[0].arguments)  # type: ignore
    assert generated_arguments["function_name"] == "GITHUB__STAR_REPOSITORY"
    assert generated_arguments["function_arguments"]["path"]["owner"] == "aipotheosis-labs"
    assert generated_arguments["function_arguments"]["path"]["repo"] == "aci"

    input_messages.append(openai_response.output[0])

    # Can't run this without a real github linked account
    # handle execute function call
    # aci_response = aci.handle_function_call(
    #     openai_response.output[0].name,
    #     json.loads(openai_response.output[0].arguments),
    #     linked_account_owner_id="python_sdk_test",
    # )
    # print(aci_response)
