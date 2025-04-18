import httpx
import pytest
import respx

from aci import ACI
from aci._constants import DEFAULT_MAX_RETRIES
from aci._exceptions import (
    AuthenticationError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    ServerError,
    UnknownError,
    ValidationError,
)
from aci.types.functions import FunctionDefinitionFormat

from .utils import MOCK_BASE_URL

MOCK_LINKED_ACCOUNT_OWNER_ID = "123"
MOCK_FUNCTION_NAME = "TEST_FUNCTION"
MOCK_FUNCTION_ARGUMENTS = {"param1": "value1", "param2": "value2"}


@respx.mock
@pytest.mark.parametrize(
    "search_params",
    [
        {},
        {
            "app_names": ["TEST"],
            "intent": "test",
            "allowed_apps_only": True,
            "format": FunctionDefinitionFormat.OPENAI,
            "limit": 10,
            "offset": 0,
        },
    ],
)
def test_search_functions_success(client: ACI, search_params: dict) -> None:
    mock_response = [{"name": "string", "description": "string"}]

    route = respx.get(f"{MOCK_BASE_URL}functions/search").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    functions = client.functions.search(**search_params)
    assert functions == mock_response
    assert route.call_count == 1, "should not retry"


@respx.mock
@pytest.mark.parametrize(
    "format, mock_response",
    [
        (
            FunctionDefinitionFormat.OPENAI,
            {
                "type": "function",
                "function": {
                    "name": "function_name",
                    "description": "function_description",
                    "parameters": {},
                },
            },
        ),
        (
            FunctionDefinitionFormat.ANTHROPIC,
            {
                "name": "function_name",
                "description": "function_description",
                "input_schema": {},
            },
        ),
    ],
)
def test_get_function_definition_success(
    client: ACI, format: FunctionDefinitionFormat, mock_response: dict
) -> None:
    route = respx.get(
        f"{MOCK_BASE_URL}functions/{MOCK_FUNCTION_NAME}/definition",
        params={"format": format.value},
    ).mock(return_value=httpx.Response(200, json=mock_response))

    response = client.functions.get_definition(MOCK_FUNCTION_NAME, format)
    assert response == mock_response
    assert route.call_count == 1, "should not retry"


@respx.mock
def test_get_function_definition_unauthorized(client: ACI) -> None:
    route = respx.get(f"{MOCK_BASE_URL}functions/{MOCK_FUNCTION_NAME}/definition").mock(
        return_value=httpx.Response(401, json={"message": "Unauthorized"})
    )

    with pytest.raises(AuthenticationError) as exc_info:
        client.functions.get_definition(MOCK_FUNCTION_NAME)

    assert "Unauthorized" in str(exc_info.value)
    assert route.call_count == 1, "should not retry"


@respx.mock
def test_get_function_definition_forbidden(client: ACI) -> None:
    route = respx.get(f"{MOCK_BASE_URL}functions/{MOCK_FUNCTION_NAME}/definition").mock(
        return_value=httpx.Response(403, json={"message": "Forbidden"})
    )

    with pytest.raises(PermissionError) as exc_info:
        client.functions.get_definition(MOCK_FUNCTION_NAME)

    assert "Forbidden" in str(exc_info.value)
    assert route.call_count == 1, "should not retry"


@respx.mock
def test_get_function_definition_not_found(client: ACI) -> None:
    route = respx.get(f"{MOCK_BASE_URL}functions/{MOCK_FUNCTION_NAME}/definition").mock(
        return_value=httpx.Response(404, json={"message": "Function not found"})
    )

    with pytest.raises(NotFoundError) as exc_info:
        client.functions.get_definition(MOCK_FUNCTION_NAME)

    assert "Function not found" in str(exc_info.value)
    assert route.call_count == 1, "should not retry"


@respx.mock
@pytest.mark.parametrize(
    "function_arguments",
    [
        {},
        MOCK_FUNCTION_ARGUMENTS,
    ],
)
def test_execute_function_success(client: ACI, function_arguments: dict) -> None:
    mock_response = {"success": True, "data": "string"}
    route = respx.post(f"{MOCK_BASE_URL}functions/{MOCK_FUNCTION_NAME}/execute").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    response = client.functions.execute(
        MOCK_FUNCTION_NAME, function_arguments, MOCK_LINKED_ACCOUNT_OWNER_ID
    )
    assert response.model_dump(exclude_none=True) == mock_response
    assert route.call_count == 1, "should not retry"


@respx.mock
def test_execute_function_bad_request(client: ACI) -> None:
    route = respx.post(f"{MOCK_BASE_URL}functions/{MOCK_FUNCTION_NAME}/execute").mock(
        return_value=httpx.Response(400, json={"message": "Bad request"})
    )

    with pytest.raises(ValidationError) as exc_info:
        client.functions.execute(
            MOCK_FUNCTION_NAME, MOCK_FUNCTION_ARGUMENTS, MOCK_LINKED_ACCOUNT_OWNER_ID
        )

    assert "Bad request" in str(exc_info.value)
    assert route.call_count == 1, "should not retry"


@respx.mock
def test_execute_function_rate_limit_exceeded(client: ACI) -> None:
    route = respx.post(f"{MOCK_BASE_URL}functions/{MOCK_FUNCTION_NAME}/execute").mock(
        return_value=httpx.Response(429, json={"message": "Rate limit exceeded"})
    )

    with pytest.raises(RateLimitError) as exc_info:
        client.functions.execute(
            MOCK_FUNCTION_NAME, MOCK_FUNCTION_ARGUMENTS, MOCK_LINKED_ACCOUNT_OWNER_ID
        )

    assert "Rate limit exceeded" in str(exc_info.value)
    assert route.call_count == DEFAULT_MAX_RETRIES, "should retry"


@respx.mock
def test_execute_function_server_error(client: ACI) -> None:
    route = respx.post(f"{MOCK_BASE_URL}functions/{MOCK_FUNCTION_NAME}/execute").mock(
        return_value=httpx.Response(500, json={"message": "Internal server error"})
    )

    with pytest.raises(ServerError) as exc_info:
        client.functions.execute(
            MOCK_FUNCTION_NAME, MOCK_FUNCTION_ARGUMENTS, MOCK_LINKED_ACCOUNT_OWNER_ID
        )

    assert route.call_count == DEFAULT_MAX_RETRIES, "should retry"
    assert "Internal server error" in str(exc_info.value)


@respx.mock
def test_execute_function_unknown_error(client: ACI) -> None:
    route = respx.post(f"{MOCK_BASE_URL}functions/{MOCK_FUNCTION_NAME}/execute").mock(
        return_value=httpx.Response(418, json={"message": "I'm a teapot"})
    )

    with pytest.raises(UnknownError):
        client.functions.execute(
            MOCK_FUNCTION_NAME, MOCK_FUNCTION_ARGUMENTS, MOCK_LINKED_ACCOUNT_OWNER_ID
        )

    assert route.call_count == DEFAULT_MAX_RETRIES, "should retry"


@respx.mock
def test_execute_function_timeout_exception(client: ACI) -> None:
    route = respx.post(f"{MOCK_BASE_URL}functions/{MOCK_FUNCTION_NAME}/execute").mock(
        side_effect=httpx.TimeoutException("Request timed out")
    )

    with pytest.raises(httpx.TimeoutException) as exc_info:
        client.functions.execute(
            MOCK_FUNCTION_NAME, MOCK_FUNCTION_ARGUMENTS, MOCK_LINKED_ACCOUNT_OWNER_ID
        )

    assert "Request timed out" in str(exc_info.value)
    assert route.call_count == DEFAULT_MAX_RETRIES, "should retry"


@respx.mock
def test_execute_function_network_error(client: ACI) -> None:
    route = respx.post(f"{MOCK_BASE_URL}functions/{MOCK_FUNCTION_NAME}/execute").mock(
        side_effect=httpx.NetworkError("Network error")
    )

    with pytest.raises(httpx.NetworkError) as exc_info:
        client.functions.execute(
            MOCK_FUNCTION_NAME, MOCK_FUNCTION_ARGUMENTS, MOCK_LINKED_ACCOUNT_OWNER_ID
        )

    assert "Network error" in str(exc_info.value)
    assert route.call_count == DEFAULT_MAX_RETRIES, "should retry"


@respx.mock
def test_execute_function_retry_on_server_error(client: ACI) -> None:
    mock_success_response = {"success": True, "data": "string"}

    # Simulate two server errors followed by a successful response
    route = respx.post(f"{MOCK_BASE_URL}functions/{MOCK_FUNCTION_NAME}/execute").mock(
        side_effect=[
            httpx.Response(500, json={"message": "Internal server error"}),
            httpx.Response(500, json={"message": "Internal server error"}),
            httpx.Response(200, json=mock_success_response),
        ]
    )

    response = client.functions.execute(
        MOCK_FUNCTION_NAME, MOCK_FUNCTION_ARGUMENTS, MOCK_LINKED_ACCOUNT_OWNER_ID
    )
    assert route.call_count == 3, "should retry until success"
    assert response.model_dump(exclude_none=True) == mock_success_response


@respx.mock
def test_execute_function_retry_exhausted(client: ACI) -> None:
    route = respx.post(f"{MOCK_BASE_URL}functions/{MOCK_FUNCTION_NAME}/execute").mock(
        side_effect=[
            httpx.Response(500, json={"message": "Internal server error"}),
            httpx.Response(500, json={"message": "Internal server error"}),
            httpx.Response(500, json={"message": "Internal server error"}),
            httpx.Response(500, json={"message": "Internal server error"}),
            httpx.Response(500, json={"message": "Internal server error"}),
        ]
    )

    with pytest.raises(ServerError) as exc_info:
        client.functions.execute(
            MOCK_FUNCTION_NAME, MOCK_FUNCTION_ARGUMENTS, MOCK_LINKED_ACCOUNT_OWNER_ID
        )

    assert route.call_count == DEFAULT_MAX_RETRIES, "should retry"
    assert "Internal server error" in str(exc_info.value)
