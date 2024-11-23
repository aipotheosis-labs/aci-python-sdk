from __future__ import annotations

import json
import logging
import os
from typing import Any

import httpx

from aipolabs.enums.function_call_type import AipolabsFunctionCallType
from aipolabs.exceptions import (
    AipolabsError,
    APIKeyNotFound,
    AuthenticationError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from aipolabs.tools.execute_function import (
    AIPOLABS_EXECUTE_FUNCTION_NAME,
    ExecuteFunctionParameters,
)
from aipolabs.tools.fetch_function_definition import (
    AIPOLABS_FETCH_FUNCTION_DEFINITION_NAME,
    FetchFunctionDefinitionParameters,
)
from aipolabs.tools.search_apps import AIPOLABS_SEARCH_APPS_NAME, SearchAppsParameters
from aipolabs.tools.search_functions import (
    AIPOLABS_SEARCH_FUNCTIONS_NAME,
    SearchFunctionsParameters,
)
from aipolabs.utils.logging import SensitiveHeadersFilter

logger: logging.Logger = logging.getLogger(__name__)
logger.addFilter(SensitiveHeadersFilter())


class Aipolabs:

    def __init__(
        self, *, api_key: str | None = None, base_url: str | httpx.URL | None = None
    ) -> None:
        """Create and initialize a new Aipolabs client.

        Args:
            api_key: The API key to use for authentication.
            base_url: The base URL to use for the API requests.
            If values are not provided it will try to read from the corresponding environment variables.


        """
        if api_key is None:
            api_key = os.environ.get("AIPOLABS_API_KEY")
        if api_key is None:
            raise APIKeyNotFound("The API key is not found.")
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("AIPOLABS_BASE_URL")
        if base_url is None:
            base_url = "https://api.aipolabs.xyz/v1"
        self.base_url = self._enforce_trailing_slash(httpx.URL(base_url))
        # TODO: currently only openai is supported
        self.inference_provider = "openai"
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
        }
        self.client = httpx.Client(base_url=self.base_url, headers=self.headers)

    def handle_function_call(
        self, function_name: str, function_parameters: dict
    ) -> tuple[AipolabsFunctionCallType, Any]:
        """Handle a function call.

        Args:
            function_name: The name of the function to call.
            function_parameters: The parameters of the function to call.

        Returns:
            A tuple with the type of the function call and the result of the function call.
        """
        logger.info(
            f"Handling function call with name: {function_name} and params: {function_parameters}"
        )
        if function_name == AIPOLABS_SEARCH_APPS_NAME:
            search_apps_parameters = SearchAppsParameters.model_validate(function_parameters)
            return AipolabsFunctionCallType.META_SEARCH, self.search_apps(search_apps_parameters)
        elif function_name == AIPOLABS_SEARCH_FUNCTIONS_NAME:
            search_functions_parameters = SearchFunctionsParameters.model_validate(
                function_parameters
            )
            return AipolabsFunctionCallType.META_SEARCH, self.search_functions(
                search_functions_parameters
            )
        elif function_name == AIPOLABS_FETCH_FUNCTION_DEFINITION_NAME:
            fetch_function_definition_parameters = FetchFunctionDefinitionParameters.model_validate(
                function_parameters
            )
            return AipolabsFunctionCallType.META_FETCH, self.fetch_function_definition(
                fetch_function_definition_parameters.function_name
            )
        elif function_name == AIPOLABS_EXECUTE_FUNCTION_NAME:

            execute_function_parameters = ExecuteFunctionParameters.model_validate(
                function_parameters
            )
            return AipolabsFunctionCallType.META_EXECUTE, self.execute_function(
                execute_function_parameters.function_name,
                execute_function_parameters.function_parameters,
            )
        else:
            # TODO: check function exist if not return AipolabsFunctionCallType.UNKNOWN
            return AipolabsFunctionCallType.DIRECT_EXECUTE, self.execute_function(
                function_name, function_parameters
            )

    def search_apps(self, params: SearchAppsParameters) -> Any:
        # TODO: exclude_unset
        logger.info(f"Searching apps with params: {params.model_dump(exclude_unset=True)}")
        response = self.client.get(
            "apps/search",
            params=params.model_dump(exclude_unset=True),
        )

        return self._handle_response(response)

    def search_functions(self, params: SearchFunctionsParameters) -> Any:
        logger.info(f"Searching functions with params: {params.model_dump(exclude_unset=True)}")
        response = self.client.get(
            "functions/search",
            params=params.model_dump(exclude_unset=True),
        )

        return self._handle_response(response)

    def fetch_function_definition(self, function_name: str) -> Any:
        logger.info(f"Fetching function definition of {function_name}")
        response = self.client.get(
            f"functions/{function_name}",
            params={"inference_provider": self.inference_provider},
        )

        return self._handle_response(response)

    def execute_function(self, function_name: str, function_parameters: dict) -> Any:
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

        return self._handle_response(response)

    def _enforce_trailing_slash(self, url: httpx.URL) -> httpx.URL:
        if url.raw_path.endswith(b"/"):
            return url
        return url.copy_with(raw_path=url.raw_path + b"/")

    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle the API response and raise appropriate exceptions if needed."""
        try:
            response_json = response.json() if response.content else None
        except json.JSONDecodeError:
            response_json = None

        error_message: str
        if isinstance(response_json, dict):
            error_message = str(
                response_json.get("message") or response_json.get("error") or response.text
            )
        else:
            error_message = response.text

        if response.status_code == 200:
            return response_json

        if response.status_code == 401:
            raise AuthenticationError(error_message, response.status_code, response.text)
        elif response.status_code == 403:
            raise PermissionError(error_message, response.status_code, response.text)
        elif response.status_code == 404:
            raise NotFoundError(error_message, response.status_code, response.text)
        elif response.status_code == 400:
            raise ValidationError(error_message, response.status_code, response.text)
        elif response.status_code == 429:
            raise RateLimitError(error_message, response.status_code, response.text)
        elif 500 <= response.status_code < 600:
            raise ServerError(error_message, response.status_code, response.text)
        else:
            raise AipolabsError(
                f"Unexpected error occurred. Status code: {response.status_code}",
                response.status_code,
                response.text,
            )
