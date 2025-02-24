import logging

import httpx
from tenacity import retry

from aipolabs.resource._base import APIResource, retry_config
from aipolabs.types.functions import (
    Function,
    FunctionExecutionParams,
    FunctionExecutionResult,
    GetFunctionDefinitionParams,
    InferenceProvider,
    SearchFunctionsParams,
)

logger: logging.Logger = logging.getLogger(__name__)


class FunctionsResource(APIResource):
    def __init__(self, httpx_client: httpx.Client) -> None:
        super().__init__(httpx_client)

    @retry(**retry_config)
    def search(
        self,
        app_names: list[str] | None = None,
        intent: str | None = None,
        configured_only: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Function]:
        """Searches for functions.

        Args:
            app_names: List of app names to filter functions by.
            intent: search results will be sorted by relevance to this intent.
            configured_only: if True, only functions whose App has been configured in the current project will be returned.
            limit: for pagination, maximum number of functions to return.
            offset: for pagination, number of functions to skip before returning results.

        Returns:
            list[Function]: List of functions matching the search criteria in the order of relevance.

        Raises:
            Various exceptions defined in _handle_response for different HTTP status codes.
        """
        validated_params = SearchFunctionsParams(
            app_names=app_names,
            intent=intent,
            configured_only=configured_only,
            limit=limit,
            offset=offset,
        ).model_dump(exclude_none=True)

        logger.info(f"Searching functions with params: {validated_params}")
        response = self._httpx_client.get(
            "functions/search",
            params=validated_params,
        )

        data: list[dict] = self._handle_response(response)
        functions = [Function.model_validate(function) for function in data]

        return functions

    @retry(**retry_config)
    def get_definition(
        self, function_name: str, inference_provider: InferenceProvider = InferenceProvider.OPENAI
    ) -> dict:
        """Retrieves the definition of a specific function.

        Args:
            function_name: Name of the function to retrieve.
            inference_provider: Decide the function definition format based on the inference provider.

        Returns:
            # TODO: specific pydantic model for returned function definition based on inference provider
            dict: JSON schema that defines the function, varies based on the inference provider.

        Raises:
            Various exceptions defined in _handle_response for different HTTP status codes.
        """
        validated_params = GetFunctionDefinitionParams(
            function_name=function_name, inference_provider=inference_provider
        )

        logger.info(
            f"Getting function definition of {validated_params.function_name}, "
            f"inference provider: {validated_params.inference_provider}"
        )
        response = self._httpx_client.get(
            f"functions/{validated_params.function_name}/definition",
            params={"inference_provider": validated_params.inference_provider.value},
        )

        function_definition: dict = self._handle_response(response)

        return function_definition

    @retry(**retry_config)
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
