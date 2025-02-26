# Aipolabs ACI Python SDK

[![PyPI version](https://img.shields.io/pypi/v/aipolabs.svg)](https://pypi.org/project/aipolabs/)

The official Python SDK for the Aipolabs ACI API.
Currently in private beta, breaking changes are expected.

The Aipolabs ACI Python SDK provides convenient access to the Aipolabs ACI REST API from any Python 3.10+
application.

## Documentation
The REST API documentation is available [here](https://docs.aci.dev/api-reference).

## Installation
```bash
pip install aipolabs
```

or with poetry:
```bash
poetry add aipolabs
```

## Usage
Aipolabs ACI platform is built with agent-first principles. Although you can call each of the APIs below any way you prefer in your application, we strongly recommend trying the [Agent-centric features](#agent-centric-features) and taking a look at the [examples](./examples/README.md) to get the most out of the platform and to enable the full potential and vision of future agentic applications.

### Client
```python
from aipolabs import ACI

client = ACI(
    # it reads from environment variable by default so you can omit it if you set it in your environment
    api_key=os.environ.get("AIPOLABS_ACI_API_KEY")
)
```

### Apps
#### Types
```python
from aipolabs.types.apps import App, AppDetails
```

#### Methods
```python
# search for apps, returns list of basic app data, sorted by relevance to the intent
# all parameters are optional
apps: list[App] = client.apps.search(
    intent="I want to search the web",
    configured_only=True,
    categories=["search"],
    limit=10,
    offset=0
)
```

```python
# get detailed information about an app, including functions supported by the app
app_details: AppDetails = client.apps.get(app_name="BRAVE_SEARCH")
```

### Functions
#### Types
```python
from aipolabs.types.functions import Function, FunctionExecutionResult, InferenceProvider
```

#### Methods
```python
# search for functions, returns list of basic function data, sorted by relevance to the intent
# all parameters are optional
functions: list[Function] = client.functions.search(
    app_names=["BRAVE_SEARCH", "TAVILY"],
    intent="I want to search the web",
    configured_only=True,
    limit=10,
    offset=0
)
```

```python
# get function definition of a specific function, this is the schema you can feed into LLM
# the actual format is defined by the inference provider
function_definition: dict = client.functions.get_definition(
    function_name="BRAVE_SEARCH__WEB_SEARCH",
    inference_provider=InferenceProvider.OPENAI
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

### Agent-centric features
The SDK provides a suite of features and helper functions to make it easier and more seamless to use functions in LLM powered agentic applications.
This is our vision and the recommended way of trying out the SDK.

#### Meta Functions and Unified Function Calling Handler
We provide 4 meta functions that can be used with LLMs as tools directly, and a unified handler for function calls. With these the LLM can discover apps and functions (that our platform supports) and execute them autonomously.

```python
from aipolabs import meta_functions

# meta functions
tools = [
    meta_functions.ACISearchApps.SCHEMA,
    meta_functions.ACISearchFunctions.SCHEMA,
    meta_functions.ACIGetFunctionDefinition.SCHEMA,
    meta_functions.ACIExecuteFunction.SCHEMA,
]
```

```python
# unified function calling handler
result = client.handle_function_call(
    tool_call.function.name,
    json.loads(tool_call.function.arguments),
    linked_account_owner_id="john_doe",
    configured_only=True,
    inference_provider=InferenceProvider.OPENAI
)
```

There are mainly two ways to use the platform with the meta functions:

- **Fully Autonomous**: Provide all 4 meta functions to the LLM, please see the [agent_with_dynamic_function_discovery_and_fixed_tools.py](./examples/agent_with_dynamic_function_discovery_and_fixed_tools.py) for more details.
- **Semi Autonomous**: Provide all but `ACIExecuteFunction` to the LLM, and use the Unified Function Calling Handler to execute functions, please see the [agent_with_dynamic_function_discovery_and_dynamic_tools.py](./examples/agent_with_dynamic_function_discovery_and_dynamic_tools.py) for more details.

Please also see [agent_with_preplanned_tools.py](./examples/agent_with_pre_planned_tools.py) for comparison where the specific functions are pre selected and provided to the LLM.

