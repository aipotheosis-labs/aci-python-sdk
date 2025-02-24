import logging
from typing import Any

import httpx
from tenacity import (
    after_log,
    before_log,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from aipolabs._constants import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_MAX_WAIT,
    DEFAULT_RETRY_MIN_WAIT,
    DEFAULT_RETRY_MULTIPLIER,
)
from aipolabs._exceptions import (
    AuthenticationError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    ServerError,
    UnknownError,
    ValidationError,
)

logger: logging.Logger = logging.getLogger(__name__)


class APIResource:
    _httpx_client: httpx.Client

    def __init__(self, httpx_client: httpx.Client) -> None:
        self._httpx_client = httpx_client

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


# Shared retry config for all requests to the Aipolabs ACI API
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
