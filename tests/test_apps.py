import httpx
import pytest
import respx

from aipolabs import Aipolabs

from .utils import MOCK_BASE_URL


@respx.mock
@pytest.mark.parametrize(
    "search_params",
    [
        {},  # Base case: No optional parameters provided.
        {  # All optional parameters provided.
            "intent": "test",
            "configured_only": True,
            "categories": ["utility", "education"],
            "limit": 10,
            "offset": 5,
        },
    ],
)
def test_search_apps_success(client: Aipolabs, search_params: dict) -> None:
    mock_response = [{"name": "Test App", "description": "Test Description"}]

    route = respx.get(f"{MOCK_BASE_URL}apps/search").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    apps = client.apps.search(**search_params)
    assert [app.model_dump() for app in apps] == mock_response
    assert route.call_count == 1, "should not retry"


@respx.mock
def test_get_app_success(client: Aipolabs) -> None:
    app_name = "TEST_APP"
    mock_response = {
        "name": "Test App",
        "description": "Test Description",
        "functions": [{"name": "Test Function", "description": "Test Description"}],
    }
    route = respx.get(f"{MOCK_BASE_URL}apps/{app_name}").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    app = client.apps.get(app_name)
    assert app.model_dump() == mock_response
    assert route.call_count == 1, "should not retry"
