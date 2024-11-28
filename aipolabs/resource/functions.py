import logging

import httpx
from tenacity import retry

from aipolabs.meta_functions import (
    AipolabsExecuteFunction,
    AipolabsGetFunctionDefinition,
    AipolabsSearchFunctions,
)
from aipolabs.resource._base import APIResource, retry_config

logger: logging.Logger = logging.getLogger(__name__)


class FunctionsResource(APIResource):
    def __init__(self, httpx_client: httpx.Client, inference_provider: str) -> None:
        super().__init__(httpx_client)
        self._inference_provider = inference_provider

    @retry(**retry_config)
    def search(
        self,
        app_names: list[str] | None = None,
        intent: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[AipolabsSearchFunctions.Function]:
        """Searches for functions using the provided parameters.

        Args:
            app_names: List of app names to filter functions by.
            intent: search results will be sorted by relevance to this intent.
            limit: for pagination, maximum number of functions to return.
            offset: for pagination, number of functions to skip before returning results.

        Returns:
            list[AipolabsSearchFunctions.Function]: List of functions matching the search criteria in the order of relevance.

        Raises:
            Various exceptions defined in _handle_response for different HTTP status codes.
        """
        validated_params = AipolabsSearchFunctions.SearchFunctionsParams(
            app_names=app_names, intent=intent, limit=limit, offset=offset
        ).model_dump(exclude_none=True)

        logger.info(f"Searching functions with params: {validated_params}")
        response = self._httpx_client.get(
            "functions/search",
            params=validated_params,
        )

        data: list[dict] = self._handle_response(response)
        functions = [AipolabsSearchFunctions.Function.model_validate(function) for function in data]

        return functions

    @retry(**retry_config)
    def get(self, function_name: str) -> dict:
        """Retrieves the definition of a specific function.

        Args:
            function_name: Name of the function to retrieve.

        Returns:
            dict: JSON schema that defines the function, varies based on the inference provider.

        Raises:
            Various exceptions defined in _handle_response for different HTTP status codes.
        """
        validated_params = AipolabsGetFunctionDefinition.GetFunctionDefinitionParams(
            function_name=function_name, inference_provider=self._inference_provider
        )

        logger.info(
            f"Getting function definition of {validated_params.function_name}, "
            f"format: {validated_params.inference_provider}"
        )
        response = self._httpx_client.get(
            f"functions/{validated_params.function_name}",
            params={"inference_provider": validated_params.inference_provider},
        )

        function_definition: dict = self._handle_response(response)

        return function_definition

    @retry(**retry_config)
    def execute(
        self, function_name: str, function_parameters: dict
    ) -> AipolabsExecuteFunction.FunctionExecutionResult:
        """Executes a Aipolabs indexed function with the provided parameters.

        Args:
            function_name: Name of the function to execute.
            function_parameters: Dictionary containing the input parameters for the function.

        Returns:
            AipolabsExecuteFunction.FunctionExecutionResult: containing the function execution results.

        Raises:
            Various exceptions defined in _handle_response for different HTTP status codes.
        """
        validated_params = AipolabsExecuteFunction.FunctionExecutionParams(
            function_name=function_name, function_parameters=function_parameters
        )

        logger.info(
            f"Executing function with name: {validated_params.function_name} and params: {validated_params.function_parameters}"
        )
        request_body = {
            "function_input": validated_params.function_parameters,
        }
        response = self._httpx_client.post(
            f"functions/{validated_params.function_name}/execute",
            json=request_body,
        )

        function_execution_result: AipolabsExecuteFunction.FunctionExecutionResult = (
            AipolabsExecuteFunction.FunctionExecutionResult.model_validate(
                self._handle_response(response)
            )
        )

        return function_execution_result
