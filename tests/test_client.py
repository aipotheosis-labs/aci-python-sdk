import httpx
import pytest

from aipolabs import ACI
from aipolabs._constants import DEFAULT_SERVER_URL
from aipolabs._exceptions import APIKeyNotFound

from .utils import MOCK_API_KEY, MOCK_BASE_URL


def test_client_initialization() -> None:
    client = ACI(api_key=MOCK_API_KEY, base_url=MOCK_BASE_URL)
    assert client.api_key == MOCK_API_KEY
    assert client.base_url == httpx.URL(MOCK_BASE_URL)
    assert client.headers["x-api-key"] == MOCK_API_KEY
    assert hasattr(client, "apps")
    assert hasattr(client, "functions")


def test_client_initialization_without_api_key() -> None:
    with pytest.raises(APIKeyNotFound):
        ACI(api_key=None, base_url=MOCK_BASE_URL)


def test_client_initialization_without_base_url() -> None:
    client = ACI(api_key=MOCK_API_KEY, base_url=None)
    assert client.base_url == httpx.URL(DEFAULT_SERVER_URL)
