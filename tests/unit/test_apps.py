import httpx
import pytest
import respx

from aci import ACI

from .utils import MOCK_BASE_URL


@respx.mock
@pytest.mark.parametrize(
    "search_params",
    [
        {},  # Base case: No optional parameters provided.
        {  # All optional parameters provided.
            "intent": "test",
            "allowed_apps_only": True,
            "include_functions": True,
            "categories": ["utility", "education"],
            "limit": 10,
            "offset": 5,
        },
    ],
)
def test_search_apps_success(client: ACI, search_params: dict) -> None:
    mock_response = [
        {
            "name": "string",
            "description": "string",
            "functions": [{"name": "string", "description": "string"}],
        }
    ]

    route = respx.get(f"{MOCK_BASE_URL}apps/search").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    apps = client.apps.search(**search_params)
    assert [app.model_dump(exclude_none=True) for app in apps] == mock_response
    assert route.call_count == 1, "should not retry"


@respx.mock
def test_get_app_success(client: ACI) -> None:
    app_name = "TEST_APP"
    mock_response = {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "name": "string",
        "display_name": "string",
        "provider": "string",
        "version": "string",
        "description": "string",
        "logo": "string",
        "categories": ["string"],
        "visibility": "public",
        "active": True,
        "security_schemes": ["no_auth"],
        "functions": [
            {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "app_name": "string",
                "name": "string",
                "description": "string",
                "tags": ["string"],
                "visibility": "public",
                "active": True,
                "protocol": "rest",
                "protocol_data": {},
                "parameters": {},
                "response": {},
            }
        ],
    }
    route = respx.get(f"{MOCK_BASE_URL}apps/{app_name}").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    app = client.apps.get(app_name)
    assert app.model_dump() == mock_response
    assert route.call_count == 1, "should not retry"
