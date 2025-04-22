from aci.types.enums import FunctionDefinitionFormat


class MetaFunctionBase:
    @classmethod
    def get_name(cls) -> str:
        """Return the name of the meta function."""
        return cls._get_base_schema()["name"]  # type: ignore

    @classmethod
    def to_json_schema(
        cls, format: FunctionDefinitionFormat = FunctionDefinitionFormat.OPENAI
    ) -> dict:
        """Generate schema in the specified format.

        Args:
            format: The schema format to use (OPENAI, ANTHROPIC, etc.)

        Returns:
            Schema formatted according to the specified format
        """
        base_schema = cls._get_base_schema()

        if format == FunctionDefinitionFormat.OPENAI:
            return {
                "type": "function",
                "function": {
                    "name": base_schema["name"],
                    "description": base_schema["description"],
                    "parameters": base_schema["parameters"],
                },
            }
        elif format == FunctionDefinitionFormat.OPENAI_RESPONSES:
            return {
                "type": "function",
                "name": base_schema["name"],
                "description": base_schema["description"],
                "parameters": base_schema["parameters"],
            }
        elif format == FunctionDefinitionFormat.ANTHROPIC:
            return {
                "name": base_schema["name"],
                "description": base_schema["description"],
                "input_schema": base_schema["parameters"],
            }
        else:
            raise ValueError(f"Unsupported schema format: {format}")

    @classmethod
    def _get_base_schema(cls) -> dict:
        """Return the base schema with name, description, and parameters.

        This must be implemented by subclasses.
        """
        raise NotImplementedError
