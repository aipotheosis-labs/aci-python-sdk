import os

import pytest

from aci import ACI
from aci.types.enums import SecurityScheme

ACI_API_KEY = os.getenv("ACI_API_KEY")

"""
The repo doesn't use load_dotenv() so we need to set the environment variables manually.
You can use something like dotenv to load the environment variables from a .env file for a single run.
e.g.

```
$ npm install -g dotenv-cli
$ dotenv run pytest tests/e2e/test_app_configurations.py -s
```
"""


@pytest.mark.skipif(ACI_API_KEY is None, reason="ACI_API_KEY is not set")
def test_app_configurations() -> None:
    aci = ACI(api_key=ACI_API_KEY)
    # step 0: make sure no app configurations exist
    assert len(aci.app_configurations.list()) == 0

    # step 1: app configurations of different types of security schemes
    gmail_configuration = aci.app_configurations.create(
        app_name="GMAIL",
        security_scheme=SecurityScheme.OAUTH2,
    )
    assert gmail_configuration.app_name == "GMAIL"
    assert gmail_configuration.security_scheme == SecurityScheme.OAUTH2

    brave_search_configuration = aci.app_configurations.create(
        app_name="BRAVE_SEARCH",
        security_scheme=SecurityScheme.API_KEY,
    )
    assert brave_search_configuration.app_name == "BRAVE_SEARCH"
    assert brave_search_configuration.security_scheme == SecurityScheme.API_KEY

    asm_configuration = aci.app_configurations.create(
        app_name="AIPOLABS_SECRETS_MANAGER",
        security_scheme=SecurityScheme.NO_AUTH,
    )
    assert asm_configuration.app_name == "AIPOLABS_SECRETS_MANAGER"
    assert asm_configuration.security_scheme == SecurityScheme.NO_AUTH

    # step 2: get a specific app configuration
    retrieved_gmail_configuration = aci.app_configurations.get(app_name="GMAIL")
    assert retrieved_gmail_configuration.app_name == "GMAIL"
    assert retrieved_gmail_configuration.security_scheme == SecurityScheme.OAUTH2

    # step 3: list all app configurations
    app_configurations = aci.app_configurations.list()
    assert len(app_configurations) == 3
    assert all(
        app_configuration.app_name in ["GMAIL", "BRAVE_SEARCH", "AIPOLABS_SECRETS_MANAGER"]
        for app_configuration in app_configurations
    )
    assert all(
        app_configuration.security_scheme
        in [SecurityScheme.OAUTH2, SecurityScheme.API_KEY, SecurityScheme.NO_AUTH]
        for app_configuration in app_configurations
    )

    # step 4: list with app name filter
    app_configurations = aci.app_configurations.list(app_names=["GMAIL", "BRAVE_SEARCH"])
    assert len(app_configurations) == 2
    assert all(
        app_configuration.app_name in ["GMAIL", "BRAVE_SEARCH"]
        for app_configuration in app_configurations
    )

    # step 5: list with limit
    app_configurations = aci.app_configurations.list(limit=1)
    assert len(app_configurations) == 1
    assert app_configurations[0].app_name in [
        "GMAIL",
        "BRAVE_SEARCH",
        "AIPOLABS_SECRETS_MANAGER",
    ]

    # step 6: delete all app configurations
    for app_name in ["GMAIL", "BRAVE_SEARCH", "AIPOLABS_SECRETS_MANAGER"]:
        aci.app_configurations.delete(app_name=app_name)
    assert len(aci.app_configurations.list()) == 0
