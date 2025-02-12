import httpx
import pytest
import respx

from aipolabs import Aipolabs
from aipolabs._constants import DEFAULT_MAX_RETRIES
from aipolabs._exceptions import (
    AuthenticationError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    ServerError,
    UnknownError,
    ValidationError,
)

from .utils import MOCK_BASE_URL

MOCK_LINKED_ACCOUNT_OWNER_ID = "123"
MOCK_FUNCTION_NAME = "TEST_FUNCTION"
MOCK_FUNCTION_PARAMETERS = {"param1": "value1", "param2": "value2"}


@respx.mock
@pytest.mark.parametrize(
    "search_params",
    [
        {},
        {
            "app_names": ["TEST"],
            "intent": "test",
            "configured_only": True,
            "limit": 10,
            "offset": 0,
        },
    ],
)
def test_search_functions_success(client: Aipolabs, search_params: dict) -> None:
    mock_response = [{"name": "string", "description": "string"}]

    route = respx.get(f"{MOCK_BASE_URL}functions/search").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    functions = client.functions.search(**search_params)
    assert [function.model_dump() for function in functions] == mock_response
    assert route.call_count == 1, "should not retry"


@respx.mock
def test_get_function_definition_success(client: Aipolabs) -> None:
    mock_response = {
        "type": "function",
        "function": {
            "name": "string",
            "strict": True,
            "description": "string",
            "parameters": {},
        },
    }
    route = respx.get(f"{MOCK_BASE_URL}functions/{MOCK_FUNCTION_NAME}/definition").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    response = client.functions.get_definition(MOCK_FUNCTION_NAME)
    assert response == mock_response
    assert route.call_count == 1, "should not retry"


@respx.mock
def test_get_function_definition_unauthorized(client: Aipolabs) -> None:
    route = respx.get(f"{MOCK_BASE_URL}functions/{MOCK_FUNCTION_NAME}/definition").mock(
        return_value=httpx.Response(401, json={"message": "Unauthorized"})
    )

    with pytest.raises(AuthenticationError) as exc_info:
        client.functions.get_definition(MOCK_FUNCTION_NAME)

    assert "Unauthorized" in str(exc_info.value)
    assert route.call_count == 1, "should not retry"


@respx.mock
def test_get_function_definition_forbidden(client: Aipolabs) -> None:
    route = respx.get(f"{MOCK_BASE_URL}functions/{MOCK_FUNCTION_NAME}/definition").mock(
        return_value=httpx.Response(403, json={"message": "Forbidden"})
    )

    with pytest.raises(PermissionError) as exc_info:
        client.functions.get_definition(MOCK_FUNCTION_NAME)

    assert "Forbidden" in str(exc_info.value)
    assert route.call_count == 1, "should not retry"


@respx.mock
def test_get_function_definition_not_found(client: Aipolabs) -> None:
    route = respx.get(f"{MOCK_BASE_URL}functions/{MOCK_FUNCTION_NAME}/definition").mock(
        return_value=httpx.Response(404, json={"message": "Function not found"})
    )

    with pytest.raises(NotFoundError) as exc_info:
        client.functions.get_definition(MOCK_FUNCTION_NAME)

    assert "Function not found" in str(exc_info.value)
    assert route.call_count == 1, "should not retry"


@respx.mock
@pytest.mark.parametrize(
    "function_parameters",
    [
        {},
        MOCK_FUNCTION_PARAMETERS,
    ],
)
def test_execute_function_success(client: Aipolabs, function_parameters: dict) -> None:
    mock_response = {"success": True, "data": "string"}
    route = respx.post(f"{MOCK_BASE_URL}functions/{MOCK_FUNCTION_NAME}/execute").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    response = client.functions.execute(
        MOCK_FUNCTION_NAME, function_parameters, MOCK_LINKED_ACCOUNT_OWNER_ID
    )
    assert response.model_dump(exclude_none=True) == mock_response
    assert route.call_count == 1, "should not retry"


@respx.mock
def test_execute_function_bad_request(client: Aipolabs) -> None:
    route = respx.post(f"{MOCK_BASE_URL}functions/{MOCK_FUNCTION_NAME}/execute").mock(
        return_value=httpx.Response(400, json={"message": "Bad request"})
    )

    with pytest.raises(ValidationError) as exc_info:
        client.functions.execute(
            MOCK_FUNCTION_NAME, MOCK_FUNCTION_PARAMETERS, MOCK_LINKED_ACCOUNT_OWNER_ID
        )

    assert "Bad request" in str(exc_info.value)
    assert route.call_count == 1, "should not retry"


@respx.mock
def test_execute_function_rate_limit_exceeded(client: Aipolabs) -> None:
    route = respx.post(f"{MOCK_BASE_URL}functions/{MOCK_FUNCTION_NAME}/execute").mock(
        return_value=httpx.Response(429, json={"message": "Rate limit exceeded"})
    )

    with pytest.raises(RateLimitError) as exc_info:
        client.functions.execute(
            MOCK_FUNCTION_NAME, MOCK_FUNCTION_PARAMETERS, MOCK_LINKED_ACCOUNT_OWNER_ID
        )

    assert "Rate limit exceeded" in str(exc_info.value)
    assert route.call_count == DEFAULT_MAX_RETRIES, "should retry"


@respx.mock
def test_execute_function_server_error(client: Aipolabs) -> None:
    route = respx.post(f"{MOCK_BASE_URL}functions/{MOCK_FUNCTION_NAME}/execute").mock(
        return_value=httpx.Response(500, json={"message": "Internal server error"})
    )

    with pytest.raises(ServerError) as exc_info:
        client.functions.execute(
            MOCK_FUNCTION_NAME, MOCK_FUNCTION_PARAMETERS, MOCK_LINKED_ACCOUNT_OWNER_ID
        )

    assert route.call_count == DEFAULT_MAX_RETRIES, "should retry"
    assert "Internal server error" in str(exc_info.value)


@respx.mock
def test_execute_function_unknown_error(client: Aipolabs) -> None:
    route = respx.post(f"{MOCK_BASE_URL}functions/{MOCK_FUNCTION_NAME}/execute").mock(
        return_value=httpx.Response(418, json={"message": "I'm a teapot"})
    )

    with pytest.raises(UnknownError):
        client.functions.execute(
            MOCK_FUNCTION_NAME, MOCK_FUNCTION_PARAMETERS, MOCK_LINKED_ACCOUNT_OWNER_ID
        )

    assert route.call_count == DEFAULT_MAX_RETRIES, "should retry"


@respx.mock
def test_execute_function_timeout_exception(client: Aipolabs) -> None:
    route = respx.post(f"{MOCK_BASE_URL}functions/{MOCK_FUNCTION_NAME}/execute").mock(
        side_effect=httpx.TimeoutException("Request timed out")
    )

    with pytest.raises(httpx.TimeoutException) as exc_info:
        client.functions.execute(
            MOCK_FUNCTION_NAME, MOCK_FUNCTION_PARAMETERS, MOCK_LINKED_ACCOUNT_OWNER_ID
        )

    assert "Request timed out" in str(exc_info.value)
    assert route.call_count == DEFAULT_MAX_RETRIES, "should retry"


@respx.mock
def test_execute_function_network_error(client: Aipolabs) -> None:
    route = respx.post(f"{MOCK_BASE_URL}functions/{MOCK_FUNCTION_NAME}/execute").mock(
        side_effect=httpx.NetworkError("Network error")
    )

    with pytest.raises(httpx.NetworkError) as exc_info:
        client.functions.execute(
            MOCK_FUNCTION_NAME, MOCK_FUNCTION_PARAMETERS, MOCK_LINKED_ACCOUNT_OWNER_ID
        )

    assert "Network error" in str(exc_info.value)
    assert route.call_count == DEFAULT_MAX_RETRIES, "should retry"


@respx.mock
def test_execute_function_retry_on_server_error(client: Aipolabs) -> None:
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
        MOCK_FUNCTION_NAME, MOCK_FUNCTION_PARAMETERS, MOCK_LINKED_ACCOUNT_OWNER_ID
    )
    assert route.call_count == 3, "should retry until success"
    assert response.model_dump(exclude_none=True) == mock_success_response


@respx.mock
def test_execute_function_retry_exhausted(client: Aipolabs) -> None:
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
            MOCK_FUNCTION_NAME, MOCK_FUNCTION_PARAMETERS, MOCK_LINKED_ACCOUNT_OWNER_ID
        )

    assert route.call_count == DEFAULT_MAX_RETRIES, "should retry"
    assert "Internal server error" in str(exc_info.value)
