# Aipolabs Python SDK

[![PyPI version](https://img.shields.io/pypi/v/aipolabs.svg)](https://pypi.org/project/aipolabs/)

The official Python SDK for the Aipolabs API.
Currently in private beta, breaking changes are expected.

The Aipolabs Python SDK provides convenient access to the Aipolabs REST API from any Python 3.10+
application.

## Documentation
The REST API documentation is available [here](https://api.aipolabs.xyz/v1/docs).

## Installation
```bash
pip install aipolabs
```

or with poetry:
```bash
poetry add aipolabs
```

## Usage
Aipolabs platform is built with agent-first principles. Although you can call each of the APIs below any way you prefer in your application, we strongly recommend taking a look at the [examples](./examples) to get the most out of the platform and to enable the full potential and vision of future agentic applications.

### Client
```python
from aipolabs import Aipolabs

client = Aipolabs(
    # it reads from environment variable by default so you can omit it if you set it in your environment
    api_key=os.environ.get("AIPOLABS_API_KEY")
)
```

### Apps
Types
```python
from aipolabs.types.apps import App
```

Methods
```python
# search for apps, returns list of apps sorted by relevance to the intent
apps: list[App] = client.apps.search(intent="I want to search the web", limit=10, offset=0)
```

#### Search

### Functions

#### Types
#### Search
#### Get FunctionDefinition
#### Execute


### Agent-centric features

#### Meta Functions

#### Unified Function Calling Handler
