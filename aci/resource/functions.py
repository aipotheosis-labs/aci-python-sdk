import logging

import httpx
from tenacity import retry

from aci.resource._base import APIResource, retry_config
from aci.types.functions import (
    FunctionDefinitionFormat,
    FunctionExecutionParams,
    FunctionExecutionResult,
    GetFunctionDefinitionParams,
    SearchFunctionsParams,
)

logger: logging.Logger = logging.getLogger(__name__)


class FunctionsResource(APIResource):
    def __init__(self, httpx_client: httpx.Client) -> None:
        super().__init__(httpx_client)

    @retry(**retry_config)  # type: ignore
    def search(
        self,
        app_names: list[str] | None = None,
        intent: str | None = None,
        allowed_apps_only: bool = False,
        format: FunctionDefinitionFormat = FunctionDefinitionFormat.OPENAI,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict]:
        """Searches for functions.
        # TODO: return specific pydantic model for returned functions based on FunctionDefinitionFormat

        Args:
            app_names: List of app names to filter functions by.
            intent: search results will be sorted by relevance to this intent.
            allowed_apps_only: If true, only returns functions of apps that are allowed by the
                agent/accessor, identified by the api key.
            limit: for pagination, maximum number of functions to return.
            offset: for pagination, number of functions to skip before returning results.

        Returns:
            list[dict]: List of functions matching the search criteria in the order of relevance.
            The format of the functions is determined by the FunctionDefinitionFormat.
        Raises:
            Various exceptions defined in _handle_response for different HTTP status codes.
        """
        validated_params = SearchFunctionsParams(
            app_names=app_names,
            intent=intent,
            allowed_apps_only=allowed_apps_only,
            format=format,
            limit=limit,
            offset=offset,
        ).model_dump(exclude_none=True, mode="json")

        logger.info(f"Searching functions with params: {validated_params}")
        response = self._httpx_client.get(
            "functions/search",
            params=validated_params,
        )

        data: list[dict] = self._handle_response(response)

        return data

    @retry(**retry_config)  # type: ignore
    def get_definition(
        self, function_name: str, format: FunctionDefinitionFormat = FunctionDefinitionFormat.OPENAI
    ) -> dict:
        """Retrieves the definition of a specific function.
        # TODO: return specific pydantic model for returned functions based on FunctionDefinitionFormat

        Args:
            function_name: Name of the function to retrieve.
            format: Decide the function definition format.

        Returns:
            # TODO: specific pydantic model for returned function definition based on FunctionDefinitionFormat
            dict: JSON schema that defines the function, varies based on the FunctionDefinitionFormat.

        Raises:
            Various exceptions defined in _handle_response for different HTTP status codes.
        """
        validated_params = GetFunctionDefinitionParams(function_name=function_name, format=format)

        logger.info(
            f"Getting function definition of {validated_params.function_name}, "
            f"format: {validated_params.format}"
        )
        response = self._httpx_client.get(
            f"functions/{validated_params.function_name}/definition",
            params={"format": validated_params.format.value},
        )

        function_definition: dict = self._handle_response(response)

        return function_definition

    @retry(**retry_config)  # type: ignore
    def execute(
        self, function_name: str, function_arguments: dict, linked_account_owner_id: str
    ) -> FunctionExecutionResult:
        """Executes a Aipolabs ACI indexed function with the provided arguments.

        Args:
            function_name: Name of the function to execute.
            function_arguments: Dictionary containing the input arguments for the function.
            linked_account_owner_id: to specify with credentials of which linked account the
                function should be executed.
        Returns:
            FunctionExecutionResult: containing the function execution results.

        Raises:
            Various exceptions defined in _handle_response for different HTTP status codes.
        """
        validated_params = FunctionExecutionParams(
            function_name=function_name,
            function_arguments=function_arguments,
            linked_account_owner_id=linked_account_owner_id,
        )

        logger.info(f"Executing function with: {validated_params.model_dump()}")
        request_body = {
            "function_input": validated_params.function_arguments,
            "linked_account_owner_id": validated_params.linked_account_owner_id,
        }
        response = self._httpx_client.post(
            f"functions/{validated_params.function_name}/execute",
            json=request_body,
        )

        function_execution_result: FunctionExecutionResult = FunctionExecutionResult.model_validate(
            self._handle_response(response)
        )

        return function_execution_result
