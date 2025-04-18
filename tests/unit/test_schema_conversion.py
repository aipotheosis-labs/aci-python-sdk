from __future__ import annotations

import pytest
from pydantic import BaseModel, ConfigDict
from typing_extensions import TypedDict

from aci import to_json_schema
from aci.types.functions import FunctionDefinitionFormat


class RequiredDict(TypedDict):
    required_int: int
    optional_str: str | None


class RequiredModel(BaseModel):
    required_int: int
    optional_str: str | None


class AllowExtraArgs(BaseModel):
    ...
    model_config = ConfigDict(extra="allow")


EXPECTED_NAME = "my_function"
EXPECTED_DESCRIPTION = "This is a test function."
EXPECTED_PARAMETERS = {
    "properties": {
        "required_int": {
            "description": "This is required_int.",
            "title": "Required Int",
            "type": "integer",
        },
        "required_dict": {
            "description": "This is required_dict.",
            "properties": {
                "required_int": {"title": "Required Int", "type": "integer"},
                "optional_str": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "title": "Optional Str",
                },
            },
            "required": ["required_int", "optional_str"],
            "title": "RequiredDict",
            "type": "object",
            "additionalProperties": False,
        },
        "required_model": {
            "description": "This is required_model.",
            "properties": {
                "required_int": {"title": "Required Int", "type": "integer"},
                "optional_str": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "title": "Optional Str",
                },
            },
            "required": ["required_int", "optional_str"],
            "title": "RequiredModel",
            "type": "object",
            "additionalProperties": False,
        },
        "allow_extra_args": {
            "description": "This is allow_extra_args.",
            "additionalProperties": True,
            "properties": {},
            "title": "AllowExtraArgs",
            "type": "object",
        },
        "optional_str_with_default": {
            "default": "default string",
            "description": "This is optional_str_with_default.",
            "title": "Optional Str With Default",
            "type": "string",
        },
    },
    "required": ["required_int", "required_dict", "required_model", "allow_extra_args"],
    "title": "my_function_args",
    "type": "object",
    "additionalProperties": False,
}

EXPECTED_JSON_SCHEMA_OPENAI_RESPONSES = {
    "type": "function",
    "name": EXPECTED_NAME,
    "description": EXPECTED_DESCRIPTION,
    "parameters": EXPECTED_PARAMETERS,
}

EXPECTED_JSON_SCHEMA_OPENAI = {
    "type": "function",
    "function": {
        "name": EXPECTED_NAME,
        "description": EXPECTED_DESCRIPTION,
        "parameters": EXPECTED_PARAMETERS,
    },
}

EXPECTED_JSON_SCHEMA_ANTHROPIC = {
    "name": EXPECTED_NAME,
    "description": EXPECTED_DESCRIPTION,
    "input_schema": EXPECTED_PARAMETERS,
}


@pytest.mark.parametrize(
    ["format", "expected_schema"],
    [
        (FunctionDefinitionFormat.OPENAI_RESPONSES, EXPECTED_JSON_SCHEMA_OPENAI_RESPONSES),
        (FunctionDefinitionFormat.OPENAI, EXPECTED_JSON_SCHEMA_OPENAI),
        (FunctionDefinitionFormat.ANTHROPIC, EXPECTED_JSON_SCHEMA_ANTHROPIC),
    ],
)
def test_schema_conversion(format: FunctionDefinitionFormat, expected_schema: dict) -> None:
    # dummy function to test the schema conversion
    def my_function(
        required_int: int,
        required_dict: RequiredDict,
        required_model: RequiredModel,
        allow_extra_args: AllowExtraArgs,
        optional_str_with_default: str = "default string",
    ) -> None:
        """This is a test function.

        Args:
            required_int: This is required_int.
            required_dict: This is required_dict.
            required_model: This is required_model.
            allow_extra_args: This is allow_extra_args.
            optional_str_with_default: This is optional_str_with_default.
        """
        pass

    # test that the schema is generated correctly
    schema = to_json_schema(my_function, format=format)
    assert schema == expected_schema
