import os
import uuid

import pytest

from aci import ACI
from aci.types.enums import SecurityScheme
from aci.types.linked_accounts import LinkedAccount

ACI_API_KEY = os.getenv("ACI_API_KEY")

"""
The codease doesn't use load_dotenv() so you need to set the environment variables manually.
You can use something like dotenv to load the environment variables from a .env file for a single run.
e.g.

```
$ npm install -g dotenv-cli
$ dotenv run pytest tests/it/test_linked_accounts.py -s
```
"""

# Test user ID to use across tests
TEST_OWNER_ID = f"test-user-{uuid.uuid4()}"


@pytest.mark.skipif(ACI_API_KEY is None, reason="ACI_API_KEY is not set")
def test_linked_accounts() -> None:
    """
    Test the linked accounts API.
    """
    aci = ACI(api_key=ACI_API_KEY)

    # step 0: make sure no app configurations exist and set up test app configurations
    assert len(aci.app_configurations.list()) == 0

    # step 1: set up app configurations with different security schemes
    aci.app_configurations.create(
        app_name="BRAVE_SEARCH",
        security_scheme=SecurityScheme.API_KEY,
    )
    aci.app_configurations.create(
        app_name="AIPOLABS_SECRETS_MANAGER",
        security_scheme=SecurityScheme.NO_AUTH,
    )

    # step 2: link accounts with different security schemes
    # Link a NO_AUTH account
    no_auth_account = aci.linked_accounts.link(
        app_name="AIPOLABS_SECRETS_MANAGER",
        linked_account_owner_id=TEST_OWNER_ID,
        security_scheme=SecurityScheme.NO_AUTH,
    )
    no_auth_account = LinkedAccount.model_validate(no_auth_account)
    assert no_auth_account.app_name == "AIPOLABS_SECRETS_MANAGER"
    assert no_auth_account.linked_account_owner_id == TEST_OWNER_ID
    assert no_auth_account.security_scheme == SecurityScheme.NO_AUTH
    assert no_auth_account.enabled is True

    # Link an API_KEY account
    # Use a placeholder API key for testing
    test_api_key = "test-api-key-" + str(uuid.uuid4())
    api_key_account = aci.linked_accounts.link(
        app_name="BRAVE_SEARCH",
        linked_account_owner_id=TEST_OWNER_ID,
        security_scheme=SecurityScheme.API_KEY,
        api_key=test_api_key,
    )
    api_key_account = LinkedAccount.model_validate(api_key_account)
    assert api_key_account.app_name == "BRAVE_SEARCH"
    assert api_key_account.linked_account_owner_id == TEST_OWNER_ID
    assert api_key_account.security_scheme == SecurityScheme.API_KEY
    assert api_key_account.enabled is True

    # Link with OAuth2 would return a URL rather than an account object
    # We're not testing this in integration tests as it requires browser interaction

    # step 3: list all linked accounts for our test user
    accounts = aci.linked_accounts.list(linked_account_owner_id=TEST_OWNER_ID)
    assert len(accounts) == 2
    assert {account.app_name for account in accounts} == {
        "BRAVE_SEARCH",
        "AIPOLABS_SECRETS_MANAGER",
    }

    # step 4: get a specific linked account
    retrieved_account = aci.linked_accounts.get(api_key_account.id)
    assert retrieved_account.id == api_key_account.id
    assert retrieved_account.app_name == "BRAVE_SEARCH"
    assert retrieved_account.linked_account_owner_id == TEST_OWNER_ID

    # step 5: list linked accounts filtered by app_name
    brave_accounts = aci.linked_accounts.list(
        app_name="BRAVE_SEARCH", linked_account_owner_id=TEST_OWNER_ID
    )
    assert len(brave_accounts) == 1
    assert brave_accounts[0].app_name == "BRAVE_SEARCH"

    # step 6: disable a linked account
    disabled_account = aci.linked_accounts.disable(api_key_account.id)
    assert disabled_account.enabled is False

    # Verify the account is disabled
    retrieved_account = aci.linked_accounts.get(api_key_account.id)
    assert retrieved_account.enabled is False

    # step 7: enable a linked account
    enabled_account = aci.linked_accounts.enable(api_key_account.id)
    assert enabled_account.enabled is True

    # Verify the account is enabled
    retrieved_account = aci.linked_accounts.get(api_key_account.id)
    assert retrieved_account.enabled is True

    # step 8: delete all linked accounts
    accounts = aci.linked_accounts.list(linked_account_owner_id=TEST_OWNER_ID)
    for account in accounts:
        aci.linked_accounts.delete(account.id)

    # Verify accounts are deleted
    accounts = aci.linked_accounts.list(linked_account_owner_id=TEST_OWNER_ID)
    assert len(accounts) == 0

    # step 9: clean up app configurations
    for app_name in ["BRAVE_SEARCH", "AIPOLABS_SECRETS_MANAGER"]:
        aci.app_configurations.delete(app_name=app_name)

    # step 10: verify app configurations are deleted
    assert len(aci.app_configurations.list()) == 0


@pytest.mark.skipif(ACI_API_KEY is None, reason="ACI_API_KEY is not set")
def test_oauth2_account_linking() -> None:
    """
    Test the linked accounts API with OAuth2.
    """
    aci = ACI(api_key=ACI_API_KEY)

    # step 0: make sure no app configurations exist and set up test app configurations
    assert len(aci.app_configurations.list()) == 0

    # step 1: create a GMAIL app configuration
    aci.app_configurations.create(
        app_name="GMAIL",
        security_scheme=SecurityScheme.OAUTH2,
    )

    # step 2: link a GMAIL account
    oauth2_account = aci.linked_accounts.link(
        app_name="GMAIL",
        linked_account_owner_id=TEST_OWNER_ID,
        security_scheme=SecurityScheme.OAUTH2,
    )
    assert isinstance(oauth2_account, str)

    # step 3: delete the GMAIL app configuration
    aci.app_configurations.delete(app_name="GMAIL")

    # step 4: verify the GMAIL app configuration is deleted
    assert len(aci.app_configurations.list()) == 0
