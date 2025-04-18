import uuid
from datetime import datetime

import httpx
import pytest
import respx

from aci import ACI
from aci.types.app_configurations import AppConfiguration
from aci.types.enums import SecurityScheme

from .utils import MOCK_BASE_URL


@respx.mock
@pytest.mark.parametrize(
    "list_params",
    [
        {},  # Base case: No optional parameters provided.
        {  # All optional parameters provided.
            "app_names": ["app1", "app2"],
            "limit": 10,
            "offset": 5,
        },
    ],
)
def test_list_app_configurations_success(client: ACI, list_params: dict) -> None:
    mock_response = [
        {
            "id": str(uuid.uuid4()),
            "project_id": str(uuid.uuid4()),
            "app_name": "app1",
            "security_scheme": "oauth2",
            "security_scheme_overrides": {},
            "enabled": True,
            "all_functions_enabled": True,
            "enabled_functions": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
    ]

    route = respx.get(f"{MOCK_BASE_URL}app-configurations").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    app_configs = client.app_configurations.list(**list_params)
    assert len(app_configs) == len(mock_response)
    assert app_configs[0].app_name == mock_response[0]["app_name"]
    assert route.call_count == 1, "should not retry"


@respx.mock
def test_get_app_configuration_success(client: ACI) -> None:
    app_name = "test_app"
    mock_response = {
        "id": str(uuid.uuid4()),
        "project_id": str(uuid.uuid4()),
        "app_name": app_name,
        "security_scheme": "oauth2",
        "security_scheme_overrides": {},
        "enabled": True,
        "all_functions_enabled": True,
        "enabled_functions": [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    route = respx.get(f"{MOCK_BASE_URL}app-configurations/{app_name}").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    app_config = client.app_configurations.get(app_name)
    assert isinstance(app_config, AppConfiguration)
    assert app_config.app_name == app_name
    assert route.call_count == 1, "should not retry"


# TODO: add coverage for security_scheme_overrides, all_functions_enabled, enabled_functions
@respx.mock
def test_create_app_configuration_success(client: ACI) -> None:
    app_name = "test_app"
    security_scheme = SecurityScheme.OAUTH2

    mock_response = {
        "id": str(uuid.uuid4()),
        "project_id": str(uuid.uuid4()),
        "app_name": app_name,
        "security_scheme": security_scheme,
        "security_scheme_overrides": {},
        "enabled": True,
        "all_functions_enabled": True,
        "enabled_functions": [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    route = respx.post(f"{MOCK_BASE_URL}app-configurations").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    app_config = client.app_configurations.create(
        app_name,
        security_scheme,
    )
    assert isinstance(app_config, AppConfiguration)
    assert app_config.app_name == app_name
    assert app_config.security_scheme == security_scheme
    assert route.call_count == 1, "should not retry"


@respx.mock
def test_delete_app_configuration_success(client: ACI) -> None:
    app_name = "test_app"

    route = respx.delete(f"{MOCK_BASE_URL}app-configurations/{app_name}").mock(
        return_value=httpx.Response(204)
    )

    client.app_configurations.delete(app_name)
    assert route.call_count == 1, "should not retry"
