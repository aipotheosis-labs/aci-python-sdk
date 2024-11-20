from __future__ import annotations

import logging
import os

import httpx

from aipolabs.exceptions import APIKeyNotFound
from aipolabs.utils.logging import SensitiveHeadersFilter

log: logging.Logger = logging.getLogger(__name__)
log.addFilter(SensitiveHeadersFilter())


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
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
        }
        self.client = httpx.Client(base_url=self.base_url, headers=self.headers)

    def _enforce_trailing_slash(self, url: httpx.URL) -> httpx.URL:
        if url.raw_path.endswith(b"/"):
            return url
        return url.copy_with(raw_path=url.raw_path + b"/")
