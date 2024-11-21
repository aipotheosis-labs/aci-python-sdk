from __future__ import annotations

import json
import logging
import os
from typing import Any

import httpx

from aipolabs.exceptions import APIKeyNotFound
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

    def __init__(self, *, api_key: str | None, base_url: str | httpx.URL | None) -> None:
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

    def handle_function_call(self, function_name: str, function_parameters_json: str) -> Any:
        logger.info(
            f"Handling function call with name: {function_name} and params: {function_parameters_json}"
        )
        if function_name == AIPOLABS_SEARCH_APPS_NAME:
            search_apps_parameters = SearchAppsParameters.model_validate_json(
                function_parameters_json, strict=True
            )
            return self.search_apps(search_apps_parameters)
        elif function_name == AIPOLABS_SEARCH_FUNCTIONS_NAME:
            search_functions_parameters = SearchFunctionsParameters.model_validate_json(
                function_parameters_json, strict=True
            )
            return self.search_functions(search_functions_parameters)
        elif function_name == AIPOLABS_FETCH_FUNCTION_DEFINITION_NAME:
            fetch_function_definition_parameters = (
                FetchFunctionDefinitionParameters.model_validate_json(
                    function_parameters_json, strict=True
                )
            )
            return self.fetch_function_definition(fetch_function_definition_parameters)
        else:
            # todo: check function exist
            return self.execute_function(function_name, function_parameters_json)

    def search_apps(self, params: SearchAppsParameters) -> Any:
        # TODO: exclude_unset
        logger.info(f"Searching apps with params: {params.model_dump(exclude_unset=True)}")
        response = self.client.get(
            "apps/search",
            params=params.model_dump(exclude_unset=True),
        )

        logger.info(f"Search apps response: {response.json()}")
        return response.json()

    def search_functions(self, params: SearchFunctionsParameters) -> Any:
        logger.info(f"Searching functions with params: {params.model_dump(exclude_unset=True)}")
        response = self.client.get(
            "functions/search",
            params=params.model_dump(exclude_unset=True),
        )
        logger.info(f"Search functions response: {response.json()}")
        return response.json()

    def fetch_function_definition(self, params: FetchFunctionDefinitionParameters) -> Any:
        logger.info(
            f"Fetching function definition with params: {params.model_dump(exclude_unset=True)}"
        )
        response = self.client.get(
            f"functions/{params.function_name}",
            params={"inference_provider": self.inference_provider},
        )
        logger.info(f"Fetch function definition response: {response.json()}")
        return response.json()

    def execute_function(self, function_name: str, function_parameters_json: str) -> Any:
        logger.info(
            f"Executing function with name: {function_name} and params: {function_parameters_json}"
        )
        request_body = {
            "function_input": json.loads(function_parameters_json),
        }
        response = self.client.post(
            f"functions/{function_name}",
            json=request_body,
        )
        logger.info(f"Execute function response: {response.json()}")
        return response.json()

    def _enforce_trailing_slash(self, url: httpx.URL) -> httpx.URL:
        if url.raw_path.endswith(b"/"):
            return url
        return url.copy_with(raw_path=url.raw_path + b"/")
