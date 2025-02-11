import httpx
import pytest

from aipolabs import Aipolabs
from aipolabs._constants import DEFAULT_AIPOLABS_BASE_URL
from aipolabs._exceptions import APIKeyNotFound

from .conftest import API_KEY, BASE_URL


def test_client_initialization() -> None:
    client = Aipolabs(api_key=API_KEY, base_url=BASE_URL)
    assert client.api_key == API_KEY
    assert client.base_url == httpx.URL(BASE_URL)
    assert client.headers["x-api-key"] == API_KEY
    assert hasattr(client, "apps")
    assert hasattr(client, "functions")


def test_client_initialization_without_api_key() -> None:
    with pytest.raises(APIKeyNotFound):
        Aipolabs(api_key=None, base_url=BASE_URL)


def test_client_initialization_without_base_url() -> None:
    client = Aipolabs(api_key=API_KEY, base_url=None)
    assert client.base_url == httpx.URL(DEFAULT_AIPOLABS_BASE_URL)
