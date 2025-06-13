import uuid
from typing import Dict
from uuid import UUID

import httpx
import pytest
import respx

from aci import ACI
from aci._exceptions import (
    NotFoundError,
    ValidationError,
)
from aci.types.enums import SecurityScheme

from .utils import MOCK_BASE_URL

MOCK_LINKED_ACCOUNT_ID = str(uuid.uuid4())
MOCK_PROJECT_ID = str(uuid.uuid4())
MOCK_APP_NAME = "test-app"
MOCK_OWNER_ID = "test-owner-id"
MOCK_API_KEY = "test-api-key"


@respx.mock
@pytest.mark.parametrize(
    "list_params",
    [
        {},  # Base case: No optional parameters provided.
        {"app_name": MOCK_APP_NAME},  # Filter by app_name
        {"linked_account_owner_id": MOCK_OWNER_ID},  # Filter by linked_account_owner_id
        {"app_name": MOCK_APP_NAME, "linked_account_owner_id": MOCK_OWNER_ID},  # Filter by both
    ],
)
def test_list_linked_accounts_success(client: ACI, list_params: Dict) -> None:
    mock_response = [
        {
            "id": MOCK_LINKED_ACCOUNT_ID,
            "project_id": MOCK_PROJECT_ID,
            "app_name": MOCK_APP_NAME,
            "linked_account_owner_id": MOCK_OWNER_ID,
            "security_scheme": SecurityScheme.API_KEY,
            "enabled": True,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
        }
    ]

    route = respx.get(f"{MOCK_BASE_URL}linked-accounts").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    linked_accounts = client.linked_accounts.list(**list_params)
    assert len(linked_accounts) == 1
    assert linked_accounts[0].app_name == MOCK_APP_NAME
    assert linked_accounts[0].linked_account_owner_id == MOCK_OWNER_ID
    assert route.call_count == 1, "should not retry"


@respx.mock
@pytest.mark.parametrize(
    "security_scheme, mock_credentials",
    [
        (
            SecurityScheme.OAUTH2,
            {"access_token": "test-oauth2-token"},
        ),
        (
            SecurityScheme.API_KEY,
            {"secret_key": "test-api-key"},
        ),
        (
            SecurityScheme.NO_AUTH,
            {},
        ),
    ],
)
def test_get_linked_account_with_credentials_success(
    client: ACI, security_scheme: SecurityScheme, mock_credentials: dict
) -> None:
    mock_response = {
        "id": MOCK_LINKED_ACCOUNT_ID,
        "project_id": MOCK_PROJECT_ID,
        "app_name": MOCK_APP_NAME,
        "linked_account_owner_id": MOCK_OWNER_ID,
        "security_scheme": security_scheme,
        "enabled": True,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
        "security_credentials": mock_credentials,
    }

    route = respx.get(f"{MOCK_BASE_URL}linked-accounts/{MOCK_LINKED_ACCOUNT_ID}").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    linked_account = client.linked_accounts.get(MOCK_LINKED_ACCOUNT_ID)
    assert linked_account.id == UUID(MOCK_LINKED_ACCOUNT_ID)
    assert linked_account.app_name == MOCK_APP_NAME
    assert linked_account.linked_account_owner_id == MOCK_OWNER_ID
    assert linked_account.security_scheme == security_scheme
    assert linked_account.security_credentials.model_dump() == mock_credentials
    assert route.call_count == 1, "should not retry"

@respx.mock
def test_get_linked_account_not_found(client: ACI) -> None:
    route = respx.get(f"{MOCK_BASE_URL}linked-accounts/{MOCK_LINKED_ACCOUNT_ID}").mock(
        return_value=httpx.Response(404, json={"message": "Linked account not found"})
    )

    with pytest.raises(NotFoundError) as exc_info:
        client.linked_accounts.get(MOCK_LINKED_ACCOUNT_ID)

    assert "Linked account not found" in str(exc_info.value)
    assert route.call_count == 1, "should not retry"


@respx.mock
def test_create_with_api_key_success(client: ACI) -> None:
    mock_response = {
        "id": MOCK_LINKED_ACCOUNT_ID,
        "project_id": MOCK_PROJECT_ID,
        "app_name": MOCK_APP_NAME,
        "linked_account_owner_id": MOCK_OWNER_ID,
        "security_scheme": SecurityScheme.API_KEY,
        "enabled": True,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
    }

    route = respx.post(f"{MOCK_BASE_URL}linked-accounts/api-key").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    result = client.linked_accounts.link(
        app_name=MOCK_APP_NAME,
        linked_account_owner_id=MOCK_OWNER_ID,
        security_scheme=SecurityScheme.API_KEY,
        api_key=MOCK_API_KEY,
    )

    assert result.id == UUID(MOCK_LINKED_ACCOUNT_ID)
    assert result.app_name == MOCK_APP_NAME
    assert result.security_scheme == SecurityScheme.API_KEY
    assert route.call_count == 1, "should not retry"


@respx.mock
def test_create_with_no_auth_success(client: ACI) -> None:
    mock_response = {
        "id": MOCK_LINKED_ACCOUNT_ID,
        "project_id": MOCK_PROJECT_ID,
        "app_name": MOCK_APP_NAME,
        "linked_account_owner_id": MOCK_OWNER_ID,
        "security_scheme": SecurityScheme.NO_AUTH,
        "enabled": True,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
    }

    route = respx.post(f"{MOCK_BASE_URL}linked-accounts/no-auth").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    result = client.linked_accounts.link(
        app_name=MOCK_APP_NAME,
        linked_account_owner_id=MOCK_OWNER_ID,
        security_scheme=SecurityScheme.NO_AUTH,
    )

    assert result.id == UUID(MOCK_LINKED_ACCOUNT_ID)
    assert result.app_name == MOCK_APP_NAME
    assert result.security_scheme == SecurityScheme.NO_AUTH
    assert route.call_count == 1, "should not retry"


@respx.mock
def test_create_with_oauth2_success(client: ACI) -> None:
    mock_response = {"url": "https://example.com/oauth2/authorize"}

    route = respx.get(f"{MOCK_BASE_URL}linked-accounts/oauth2").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    result = client.linked_accounts.link(
        app_name=MOCK_APP_NAME,
        linked_account_owner_id=MOCK_OWNER_ID,
        security_scheme=SecurityScheme.OAUTH2,
    )

    assert result == "https://example.com/oauth2/authorize"
    assert route.call_count == 1, "should not retry"


@respx.mock
def test_create_api_key_validation_error(client: ACI) -> None:
    with pytest.raises(ValueError) as exc_info:
        client.linked_accounts.link(
            app_name=MOCK_APP_NAME,
            linked_account_owner_id=MOCK_OWNER_ID,
            security_scheme=SecurityScheme.API_KEY,
            # missing api_key
        )

    assert "api_key parameter is required" in str(exc_info.value)


@respx.mock
def test_create_with_api_key_bad_request(client: ACI) -> None:
    route = respx.post(f"{MOCK_BASE_URL}linked-accounts/api-key").mock(
        return_value=httpx.Response(400, json={"message": "Bad request"})
    )

    with pytest.raises(ValidationError) as exc_info:
        client.linked_accounts.link(
            app_name=MOCK_APP_NAME,
            linked_account_owner_id=MOCK_OWNER_ID,
            security_scheme=SecurityScheme.API_KEY,
            api_key=MOCK_API_KEY,
        )

    assert "Bad request" in str(exc_info.value)
    assert route.call_count == 1, "should not retry"


@respx.mock
def test_delete_linked_account_success(client: ACI) -> None:
    route = respx.delete(f"{MOCK_BASE_URL}linked-accounts/{MOCK_LINKED_ACCOUNT_ID}").mock(
        return_value=httpx.Response(204)
    )

    client.linked_accounts.delete(MOCK_LINKED_ACCOUNT_ID)
    assert route.call_count == 1, "should not retry"


@respx.mock
def test_delete_linked_account_not_found(client: ACI) -> None:
    route = respx.delete(f"{MOCK_BASE_URL}linked-accounts/{MOCK_LINKED_ACCOUNT_ID}").mock(
        return_value=httpx.Response(404, json={"message": "Linked account not found"})
    )

    with pytest.raises(NotFoundError) as exc_info:
        client.linked_accounts.delete(MOCK_LINKED_ACCOUNT_ID)

    assert "Linked account not found" in str(exc_info.value)
    assert route.call_count == 1, "should not retry"


@respx.mock
def test_enable_linked_account_success(client: ACI) -> None:
    mock_response = {
        "id": MOCK_LINKED_ACCOUNT_ID,
        "project_id": MOCK_PROJECT_ID,
        "app_name": MOCK_APP_NAME,
        "linked_account_owner_id": MOCK_OWNER_ID,
        "security_scheme": SecurityScheme.API_KEY,
        "enabled": True,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
    }

    route = respx.patch(f"{MOCK_BASE_URL}linked-accounts/{MOCK_LINKED_ACCOUNT_ID}").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    result = client.linked_accounts.enable(MOCK_LINKED_ACCOUNT_ID)

    assert result.id == UUID(MOCK_LINKED_ACCOUNT_ID)
    assert result.enabled is True
    assert route.call_count == 1, "should not retry"


@respx.mock
def test_disable_linked_account_success(client: ACI) -> None:
    mock_response = {
        "id": MOCK_LINKED_ACCOUNT_ID,
        "project_id": MOCK_PROJECT_ID,
        "app_name": MOCK_APP_NAME,
        "linked_account_owner_id": MOCK_OWNER_ID,
        "security_scheme": SecurityScheme.API_KEY,
        "enabled": False,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
    }

    route = respx.patch(f"{MOCK_BASE_URL}linked-accounts/{MOCK_LINKED_ACCOUNT_ID}").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    result = client.linked_accounts.disable(MOCK_LINKED_ACCOUNT_ID)

    assert result.id == UUID(MOCK_LINKED_ACCOUNT_ID)
    assert result.enabled is False
    assert route.call_count == 1, "should not retry"


@respx.mock
def test_server_error_retry(client: ACI) -> None:
    mock_success_response = {
        "id": MOCK_LINKED_ACCOUNT_ID,
        "project_id": MOCK_PROJECT_ID,
        "app_name": MOCK_APP_NAME,
        "linked_account_owner_id": MOCK_OWNER_ID,
        "security_scheme": SecurityScheme.API_KEY,
        "security_credentials": {"secret_key": "test-api-key"},
        "enabled": True,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
    }

    # Simulate two server errors followed by a successful response
    route = respx.get(f"{MOCK_BASE_URL}linked-accounts/{MOCK_LINKED_ACCOUNT_ID}").mock(
        side_effect=[
            httpx.Response(500, json={"message": "Internal server error"}),
            httpx.Response(500, json={"message": "Internal server error"}),
            httpx.Response(200, json=mock_success_response),
        ]
    )

    linked_account = client.linked_accounts.get(MOCK_LINKED_ACCOUNT_ID)

    assert route.call_count == 3, "should retry until success"
    assert linked_account.id == UUID(MOCK_LINKED_ACCOUNT_ID)


@respx.mock
def test_rate_limit_retry(client: ACI) -> None:
    mock_success_response = {
        "id": MOCK_LINKED_ACCOUNT_ID,
        "project_id": MOCK_PROJECT_ID,
        "app_name": MOCK_APP_NAME,
        "linked_account_owner_id": MOCK_OWNER_ID,
        "security_scheme": SecurityScheme.API_KEY,
        "security_credentials": {"secret_key": "test-api-key"},
        "enabled": True,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
    }

    # Simulate rate limit error followed by a successful response
    route = respx.get(f"{MOCK_BASE_URL}linked-accounts/{MOCK_LINKED_ACCOUNT_ID}").mock(
        side_effect=[
            httpx.Response(429, json={"message": "Rate limit exceeded"}),
            httpx.Response(200, json=mock_success_response),
        ]
    )

    linked_account = client.linked_accounts.get(MOCK_LINKED_ACCOUNT_ID)

    assert route.call_count == 2, "should retry after rate limit"
    assert linked_account.id == UUID(MOCK_LINKED_ACCOUNT_ID)
