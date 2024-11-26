from __future__ import annotations

import logging
import os
from typing import Any

import httpx
from tenacity import (
    after_log,
    before_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from aipolabs._constants import (
    DEFAULT_AIPOLABS_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_MAX_WAIT,
    DEFAULT_RETRY_MIN_WAIT,
    DEFAULT_RETRY_MULTIPLIER,
)
from aipolabs._exceptions import (
    APIKeyNotFound,
    AuthenticationError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    ServerError,
    UnknownError,
    ValidationError,
)
from aipolabs.meta_functions import (
    AipolabsExecuteFunction,
    AipolabsGetFunctionDefinition,
    AipolabsSearchApps,
    AipolabsSearchFunctions,
)
from aipolabs.utils._logging import SensitiveHeadersFilter

logger: logging.Logger = logging.getLogger(__name__)
logger.addFilter(SensitiveHeadersFilter())


# Shared retry config for all requests to the Aipolabs API
retry_config = {
    "stop": stop_after_attempt(DEFAULT_MAX_RETRIES),
    "wait": wait_exponential(
        multiplier=DEFAULT_RETRY_MULTIPLIER,
        min=DEFAULT_RETRY_MIN_WAIT,
        max=DEFAULT_RETRY_MAX_WAIT,
    ),
    "retry": retry_if_exception_type(
        (
            ServerError,
            RateLimitError,
            UnknownError,
            httpx.TimeoutException,
            httpx.NetworkError,
        )
    ),
    "before": before_log(logger, logging.DEBUG),
    "after": after_log(logger, logging.DEBUG),
    "reraise": True,
}


class Aipolabs:
    """Client for interacting with the Aipolabs API.

    This class provides methods to interact with various Aipolabs API endpoints,
    including searching apps and functions, getting function definitions, and
    executing functions.

    Attributes:
        api_key (str): The API key used for authentication.
        base_url (str | httpx.URL): The base URL for API requests.
        inference_provider (str): The inference provider (currently only 'openai').
        headers (dict): HTTP headers used in requests.
        client (httpx.Client): The HTTP client for making requests.
    """

    def __init__(
        self, *, api_key: str | None = None, base_url: str | httpx.URL | None = None
    ) -> None:
        """Create and initialize a new Aipolabs client.

        Args:
            api_key: The API key to use for authentication.
            base_url: The base URL to use for the API requests.
            If values are not provided it will try to read from the corresponding environment variables.
            If no value found for api_key, it will raise APIKeyNotFound.
            If no value found for base_url, it will use the default value.
        """
        if api_key is None:
            api_key = os.environ.get("AIPOLABS_API_KEY")
        if api_key is None:
            raise APIKeyNotFound("The API key is not found.")
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("AIPOLABS_BASE_URL", DEFAULT_AIPOLABS_BASE_URL)
        self.base_url = self._enforce_trailing_slash(httpx.URL(base_url))
        # TODO: currently only openai is supported
        self.inference_provider = "openai"
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
        }
        self.client = httpx.Client(base_url=self.base_url, headers=self.headers)

    def handle_function_call(self, function_name: str, function_parameters: dict) -> Any:
        """Routes and executes function calls based on the function name.
        This can be a convenience function to handle function calls from LLM without you checking the function name.

        It supports handling built-in meta functions (AIPOLABS_SEARCH_APPS, AIPOLABS_SEARCH_FUNCTIONS,
        AIPOLABS_GET_FUNCTION_DEFINITION, AIPOLABS_EXECUTE_FUNCTION) and also handling executing third-party functions
        directly like BRAVE_SEARCH__WEB_SEARCH.

        Args:
            function_name: Name of the function to be called.
            function_parameters: Dictionary containing the parameters for the function.

        Returns:
            Any: The result of the function execution. It varies based on the function.
        """
        logger.info(
            f"Handling function call with name: {function_name} and params: {function_parameters}"
        )
        if function_name == AipolabsSearchApps.NAME:
            search_apps_parameters = AipolabsSearchApps.validate_params(function_parameters)
            apps = self.search_apps(search_apps_parameters)

            return [app.model_dump() for app in apps]

        elif function_name == AipolabsSearchFunctions.NAME:
            search_functions_parameters = AipolabsSearchFunctions.validate_params(
                function_parameters
            )
            functions = self.search_functions(search_functions_parameters)

            return [function.model_dump() for function in functions]

        elif function_name == AipolabsGetFunctionDefinition.NAME:
            get_function_definition_parameters = AipolabsGetFunctionDefinition.validate_params(
                function_parameters
            )
            function_definition: dict = self.get_function_definition(
                get_function_definition_parameters.function_name
            )

            return function_definition

        elif function_name == AipolabsExecuteFunction.NAME:
            execute_function_parameters = AipolabsExecuteFunction.validate_params(
                function_parameters
            )

            function_execution_result = self.execute_function(
                execute_function_parameters.function_name,
                execute_function_parameters.function_parameters,
            )

            return function_execution_result.model_dump(exclude_none=True)

        else:
            # TODO: check function exist if not throw excpetion?
            function_execution_result = self.execute_function(function_name, function_parameters)

            return function_execution_result.model_dump(exclude_none=True)

    @retry(**retry_config)
    def search_apps(
        self, params: AipolabsSearchApps.SearchAppsParams
    ) -> list[AipolabsSearchApps.App]:
        """Searches for apps using the provided parameters.

        Args:
            params: Search parameters for filtering and sorting results.

        Returns:
            list[AipolabsSearchApps.App]: List of apps matching the search criteria in the order of relevance.

        Raises:
            Various exceptions defined in _handle_response for different HTTP status codes.
        """
        # TODO: exclude_unset
        logger.info(f"Searching apps with params: {params.model_dump(exclude_unset=True)}")
        response = self.client.get(
            "apps/search",
            params=params.model_dump(exclude_unset=True),
        )

        data: list[dict] = self._handle_response(response)
        apps = [AipolabsSearchApps.App.model_validate(app) for app in data]

        return apps

    @retry(**retry_config)
    def search_functions(
        self, params: AipolabsSearchFunctions.SearchFunctionsParams
    ) -> list[AipolabsSearchFunctions.Function]:
        """Searches for functions using the provided parameters.

        Args:
            params: Search parameters for filtering functions.

        Returns:
            list[AipolabsSearchFunctions.Function]: List of functions matching the search criteria in the order of relevance.

        Raises:
            Various exceptions defined in _handle_response for different HTTP status codes.
        """
        logger.info(f"Searching functions with params: {params.model_dump(exclude_unset=True)}")
        response = self.client.get(
            "functions/search",
            params=params.model_dump(exclude_unset=True),
        )

        data: list[dict] = self._handle_response(response)
        functions = [AipolabsSearchFunctions.Function.model_validate(function) for function in data]

        return functions

    @retry(**retry_config)
    def get_function_definition(self, function_name: str) -> dict:
        """Retrieves the definition of a specific function.

        Args:
            function_name: Name of the function to retrieve.

        Returns:
            dict: JSON schema that defines the function, varies based on the inference provider.

        Raises:
            Various exceptions defined in _handle_response for different HTTP status codes.
        """
        logger.info(f"Getting function definition of {function_name}")
        response = self.client.get(
            f"functions/{function_name}",
            params={"inference_provider": self.inference_provider},
        )

        function_definition: dict = self._handle_response(response)

        return function_definition

    @retry(**retry_config)
    def execute_function(
        self, function_name: str, function_parameters: dict
    ) -> AipolabsExecuteFunction.FunctionExecutionResult:
        """Executes a function with the provided parameters.

        Args:
            function_name: Name of the function to execute.
            function_parameters: Dictionary containing the parameters for the function.

        Returns:
            Any: JSON response containing the function execution results.

        Raises:
            Various exceptions defined in _handle_response for different HTTP status codes.
        """
        logger.info(
            f"Executing function with name: {function_name} and params: {function_parameters}"
        )
        request_body = {
            "function_input": function_parameters,
        }
        response = self.client.post(
            f"functions/{function_name}/execute",
            json=request_body,
        )

        function_execution_result: AipolabsExecuteFunction.FunctionExecutionResult = (
            AipolabsExecuteFunction.FunctionExecutionResult.model_validate(
                self._handle_response(response)
            )
        )

        return function_execution_result

    def _enforce_trailing_slash(self, url: httpx.URL) -> httpx.URL:
        """Ensures the URL ends with a trailing slash.

        Args:
            url: The URL to process.

        Returns:
            httpx.URL: URL with a guaranteed trailing slash.
        """
        if url.raw_path.endswith(b"/"):
            return url
        return url.copy_with(raw_path=url.raw_path + b"/")

    def _handle_response(self, response: httpx.Response) -> Any:
        """Processes API responses and handles errors.

        Args:
            response: The HTTP response from the API.

        Returns:
            Any: Parsed JSON response for successful requests.

        Raises:
            AuthenticationError: For 401 status codes.
            PermissionError: For 403 status codes.
            NotFoundError: For 404 status codes.
            ValidationError: For 400 status codes.
            RateLimitError: For 429 status codes.
            ServerError: For 5xx status codes.
            UnknownError: For unexpected status codes.
        """

        try:
            response.raise_for_status()
            return self._get_response_data(response)

        except httpx.HTTPStatusError as e:
            error_message = self._get_error_message(response, e)

            # TODO: cross-check with backend
            if response.status_code == 401:
                raise AuthenticationError(error_message)
            elif response.status_code == 403:
                raise PermissionError(error_message)
            elif response.status_code == 404:
                raise NotFoundError(error_message)
            elif response.status_code == 400:
                raise ValidationError(error_message)
            elif response.status_code == 429:
                raise RateLimitError(error_message)
            elif 500 <= response.status_code < 600:
                raise ServerError(error_message)
            else:
                raise UnknownError(error_message)

    def _get_response_data(self, response: httpx.Response) -> Any:
        """Get the response data from the response.
        If the response is json, return the json data, otherwise fallback to the text.
        TODO: handle non-json response?
        """
        try:
            response_data = response.json() if response.content else {}
        except Exception as e:
            logger.warning(f"error parsing json response: {str(e)}")
            response_data = response.text

        return response_data

    def _get_error_message(self, response: httpx.Response, error: httpx.HTTPStatusError) -> str:
        """Get the error message from the response or fallback to the error message from the HTTPStatusError.
        Usually the response json contains more details about the error.
        """
        try:
            return str(response.json())
        except Exception:
            return str(error)
