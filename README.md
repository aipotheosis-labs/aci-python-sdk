# ACI Python SDK

[![PyPI version](https://img.shields.io/pypi/v/aci-sdk.svg)](https://pypi.org/project/aci-sdk/)

The official Python SDK for the ACI (Agent-Computer Interface) by Aipolabs.
Currently in beta, breaking changes are expected.

The ACI Python SDK provides convenient access to the ACI REST API from any Python 3.10+
application.

## Documentation
The detailed documentation is available [here](https://aci.dev/docs).

## Installation
```bash
pip install aci-sdk
```

or with uv:
```bash
uv add aci-sdk
```

## Usage
ACI platform is built with agent-first principles. Although you can call each of the APIs below any way you prefer in your application, we strongly recommend trying the [Agent-centric features](#agent-centric-features) and taking a look at the [agent examples](https://github.com/aipotheosis-labs/aci-agents/tree/main/examples) to get the most out of the platform and to enable the full potential and vision of future agentic applications.

### Client
```python
from aci import ACI

client = ACI(
    # it reads from environment variable by default so you can omit it if you set it in your environment
    api_key=os.environ.get("ACI_API_KEY")
)
```

### Apps
#### Types
```python
from aci.types.apps import AppBasic, AppDetails
```

#### Methods
```python
# search for apps, returns list of basic app data, sorted by relevance to the intent
# all parameters are optional
apps: list[AppBasic] = client.apps.search(
    intent="I want to search the web",
    allowed_apps_only=False, # If true, only return apps that are allowed by the agent/accessor, identified by the api key.
    include_functions=False, # If true, include functions (name and description) in the search results.
    categories=["search"],
    limit=10,
    offset=0
)
```

```python
# get detailed information about an app, including functions supported by the app
app_details: AppDetails = client.apps.get(app_name="BRAVE_SEARCH")
```

### App Configurations
#### Types
```python
from aci.types.app_configurations import AppConfiguration
from aci.types.enums import SecurityScheme
```

#### Methods
```python
# Create a new app configuration
configuration = client.app_configurations.create(
    app_name="GMAIL",
    security_scheme=SecurityScheme.OAUTH2
)
```

```python
# List app configurations
# All parameters are optional
configurations: list[AppConfiguration] = client.app_configurations.list(
    app_names=["GMAIL", "BRAVE_SEARCH"],  # Filter by app names
    limit=10,  # Maximum number of results
    offset=0   # Pagination offset
)
```

```python
# Get app configuration by app name
configuration: AppConfiguration = client.app_configurations.get(app_name="GMAIL")
```


```python
# Delete an app configuration
client.app_configurations.delete(app_name="GMAIL")
```

### Linked Accounts
#### Types
```python
from aci.types.linked_accounts import LinkedAccount
from aci.types.enums import SecurityScheme
```

#### Methods
```python
# Link an account
# Returns created LinkedAccount for API_KEY and NO_AUTH security schemes
# Returns authorization URL string for OAUTH2 security scheme (you need to finish the flow in browser to create the account)
result = client.linked_accounts.link(
    app_name="BRAVE_SEARCH",                  # Name of the app to link to
    linked_account_owner_id="user123",        # ID to identify the owner of this linked account
    security_scheme=SecurityScheme.API_KEY,   # Type of authentication
    api_key="your-api-key"                    # Required for API_KEY security scheme
)

# OAuth2 example (returns auth URL for user to complete OAuth flow in browser)
oauth_url = client.linked_accounts.link(
    app_name="GMAIL",
    linked_account_owner_id="user123",
    security_scheme=SecurityScheme.OAUTH2,
    # Optional parameter to redirect to a custom URL after the OAuth2 flow (default to https://platform.aci.dev)
    after_oauth2_link_redirect_url="https://<your website for your end users>"
)

# No-auth example
account = client.linked_accounts.link(
    app_name="AGENT_SECRETS_MANAGER",
    linked_account_owner_id="user123",
    security_scheme=SecurityScheme.NO_AUTH
)
```

```python
# List linked accounts
# All parameters are optional
accounts: list[LinkedAccount] = client.linked_accounts.list(
    app_name="BRAVE_SEARCH",                  # Filter by app name
    linked_account_owner_id="user123"         # Filter by owner ID
)
```

```python
# Get a specific linked account by ID (note: linked_account_id is different from the linked_account_owner_id)
account: LinkedAccount = client.linked_accounts.get(linked_account_id=account_id)
```

```python
# Enable a linked account (note: linked_account_id is different from the linked_account_owner_id)
account: LinkedAccount = client.linked_accounts.enable(linked_account_id=account_id)
```

```python
# Disable a linked account (note: linked_account_id is different from the linked_account_owner_id)
account: LinkedAccount = client.linked_accounts.disable(linked_account_id=account_id)
```

```python
# Delete a linked account (note: linked_account_id is different from the linked_account_owner_id)
client.linked_accounts.delete(linked_account_id=account_id)
```

### Functions
#### Types
```python
from aci.types.functions import FunctionExecutionResult
from aci.types.enums import FunctionDefinitionFormat
```

#### Methods
```python
# search for functions, returns list of basic function data, sorted by relevance to the intent
# all parameters are optional
functions: list[dict] = client.functions.search(
    app_names=["BRAVE_SEARCH", "TAVILY"],
    intent="I want to search the web",
    allowed_apps_only=False, # If true, only returns functions of apps that are allowed by the agent/accessor, identified by the api key.
    format=FunctionDefinitionFormat.OPENAI, # The format of the functions, can be OPENAI, ANTHROPIC, BASIC (name and description only)
    limit=10,
    offset=0
)
```

```python
# get function definition of a specific function, this is the schema you can feed into LLM
# the actual format is defined by the format parameter: OPENAI, ANTHROPIC, BASIC (name and description only)
function_definition: dict = client.functions.get_definition(
    function_name="BRAVE_SEARCH__WEB_SEARCH",
    format=FunctionDefinitionFormat.OPENAI
)
```

```python
# execute a function with the provided parameters
result: FunctionExecutionResult = client.functions.execute(
    function_name="BRAVE_SEARCH__WEB_SEARCH",
    function_parameters={"query": {"q": "what is the weather in barcelona"}},
    linked_account_owner_id="john_doe"
)

if result.success:
    print(result.data)
else:
    print(result.error)
```

### Utility functions
#### to_json_schema
Convert a local python function to a LLM compatible tool schema, so you can use custom functions (tools) along with ACI.dev functions (tools).
```python
from aci import to_json_schema

# dummy function to test the schema conversion
def custom_function(
    required_int: int,
    optional_str_with_default: str = "default string",
) -> None:
    """This is a test function.

    Args:
        required_int: This is required_int.
        optional_str_with_default: This is optional_str_with_default.
    """
    pass

# for openai chat completions api
custom_function_openai_chat_completions = to_json_schema(custom_function, FunctionDefinitionFormat.OPENAI)
"""result:
{
    "type": "function",
    "function": {
        "name": "custom_function",
        "description": "This is a test function.",
        "parameters": {
            "properties": {
                "required_int": {
                    "description": "This is required_int.",
                    "title": "Required Int",
                    "type": "integer"
                },
                "optional_str_with_default": {
                    "default": "default string",
                    "description": "This is optional_str_with_default.",
                    "title": "Optional Str With Default",
                    "type": "string"
                }
            },
            "required": ["required_int"],
            "title": "custom_function_args",
            "type": "object",
            "additionalProperties": False
        }
    }
}
"""

# alternative format: for openai responses api
custom_function_openai_responses = to_json_schema(custom_function, FunctionDefinitionFormat.OPENAI_RESPONSES)

# alternative format: for anthropic api
custom_function_anthropic = to_json_schema(custom_function, FunctionDefinitionFormat.ANTHROPIC)

# use the tool in a openai chat completion api
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant with access to a variety of tools.",
        },
    ],
    tools=[custom_function_openai_chat_completions]
)
```

### Agent-centric features

The SDK provides a suite of features and helper functions to make it easier and more seamless to use functions in LLM powered agentic applications.
This is our vision and the recommended way of trying out the SDK.

#### Meta Functions and Unified Function Calling Handler

- A set of meta functions that can be used with LLMs as tools directly. Essentially, they are just the json schema version of some of the backend APIs of ACI.dev. They are provided so that your LLM/Agent can utlize some of the features of ACI.dev directly via function (tool) calling.

- A unified handler for function (tool) calls, which handles both the direct function calls (e.g., BRAVE_SEARCH__WEB_SEARCH) and the meta functions calls (e.g., ACISearchFunctions, ACIExecuteFunction).

```python
from aci.meta_functions import ACISearchFunctions, ACIExecuteFunction
from aci.types.enums import FunctionDefinitionFormat

# meta functions
tools = [
    ACISearchFunctions.to_json_schema(FunctionDefinitionFormat.OPENAI),
    ACIExecuteFunction.to_json_schema(FunctionDefinitionFormat.OPENAI),
]

# use the meta functions (tools) in a openai chat completion api
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": "Can you help star aipotheosis-labs/aci github repo?",
        },
    ],
    tools=tools
)
```

```python
# unified function calling handler
tool_call = response.choices[0].message.tool_calls[0]

result = client.handle_function_call(
    tool_call.function.name,
    json.loads(tool_call.function.arguments),
    linked_account_owner_id="john_doe",
    allowed_apps_only=True,
    format=FunctionDefinitionFormat.OPENAI
)
```

Please see [agent examples](https://github.com/aipotheosis-labs/aci-agents?tab=readme-ov-file#2-agent-with-dynamic-tool-discovery-and-execution) for more advanced and complete examples.
