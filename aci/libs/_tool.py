from __future__ import annotations

from typing import Any, Callable, Optional

from aci.types.functions import FunctionDefinitionFormat

from ._function_schema import DocstringStyle, function_schema

"""
This file is a modified version of the `tool.py` file from the `openai` library.
https://github.com/openai/openai-agents-python/blob/064e25b01b5c82c08aea66ff898ff27adbb013d8/src/agents/tool.py
It is used to convert a Python function to an LLM tool schema in the specified format.
"""


def to_json_schema(
    func: Callable[..., Any],
    format: FunctionDefinitionFormat,
    *,
    name_override: Optional[str] = None,
    description_override: Optional[str] = None,
    docstring_style: Optional[DocstringStyle] = None,
    use_docstring_info: bool = True,
) -> dict:
    """
    Convert a Python function to an LLM tool schema in the specified format.

    Args:
        func: The function to convert to a schema
        format: The schema format to generate, one of the following:
            - FunctionDefinitionFormat.OPENAI: for openai chat completions api
            - FunctionDefinitionFormat.OPENAI_RESPONSES: for openai responses api
            - FunctionDefinitionFormat.ANTHROPIC: for anthropic api
        name_override: Optional custom name for the function
        description_override: Optional custom description
        docstring_style: Optional docstring style for parsing
        use_docstring_info: Whether to use function docstring for descriptions

    Returns:
        A dictionary containing the tool schema in the requested format

    Examples:
        >>> def get_weather(location: str) -> str:
        ...     '''Get current temperature for a location.'''
        ...     return f"Weather information for {location}"
        ...
        >>> openai_schema = to_llm_schema(get_weather, FunctionDefinitionFormat.OPENAI)
        >>> openai_responses_schema = to_llm_schema(get_weather, FunctionDefinitionFormat.OPENAI_RESPONSES)
        >>> anthropic_schema = to_llm_schema(get_weather, FunctionDefinitionFormat.ANTHROPIC)
    """
    # Extract base function metadata
    base_schema = function_schema(
        func=func,
        name_override=name_override,
        description_override=description_override,
        docstring_style=docstring_style,
        use_docstring_info=use_docstring_info,
    )

    # Generate schema based on format
    if format == FunctionDefinitionFormat.OPENAI:
        return {
            "type": "function",
            "function": {
                "name": base_schema.name,
                "description": base_schema.description or "",
                "parameters": base_schema.params_json_schema,
            },
        }
    elif format == FunctionDefinitionFormat.OPENAI_RESPONSES:
        return {
            "type": "function",
            "name": base_schema.name,
            "description": base_schema.description or "",
            "parameters": base_schema.params_json_schema,
        }
    elif format == FunctionDefinitionFormat.ANTHROPIC:
        return {
            "name": base_schema.name,
            "description": base_schema.description or "",
            "input_schema": base_schema.params_json_schema,
        }
    else:
        # This should never happen due to type restrictions, but just in case
        raise ValueError(f"Unsupported schema format: {format}")
