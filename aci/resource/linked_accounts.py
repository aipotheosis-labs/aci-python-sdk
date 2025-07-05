import logging
from typing import List
from uuid import UUID

from httpx import Response
from tenacity import retry

from aci._constants import DEFAULT_AFTER_OAUTH2_FLOW_REDIRECT_URL
from aci.resource._base import APIResource, retry_config
from aci.types.enums import SecurityScheme
from aci.types.linked_accounts import (
    LinkedAccount,
    LinkedAccountAPIKeyCreate,
    LinkedAccountNoAuthCreate,
    LinkedAccountOAuth2Create,
    LinkedAccountsList,
    LinkedAccountUpdate,
    LinkedAccountWithCredentials,
)

logger: logging.Logger = logging.getLogger(__name__)


class LinkedAccountsResource(APIResource):
    """Resource for managing linked accounts."""

    @retry(**retry_config)  # type: ignore
    def list(
        self,
        app_name: str | None = None,
        linked_account_owner_id: str | None = None,
    ) -> List[LinkedAccount]:
        """List linked accounts.

        Args:
            app_name: Filter by app name.
            linked_account_owner_id: Filter by linked account owner ID.
            See https://www.aci.dev/docs/core-concepts/linked-account#what-is-linked-account-owner-id

        Returns:
            List[LinkedAccount]: List of linked accounts.

        Raises:
            Various exceptions defined in _handle_response for different HTTP status codes.
        """
        params = LinkedAccountsList(
            app_name=app_name,
            linked_account_owner_id=linked_account_owner_id,
        ).model_dump(exclude_none=True, mode="json")

        logger.info(f"Listing linked accounts with params: {params}")
        response = self._httpx_client.get("linked-accounts", params=params)

        data: List[dict] = self._handle_response(response)
        linked_accounts = [LinkedAccount.model_validate(account) for account in data]

        return linked_accounts

    @retry(**retry_config)  # type: ignore
    def get(self, linked_account_id: UUID) -> LinkedAccountWithCredentials:
        """Get a linked account by its ID.

        Args:
            linked_account_id: ID of the linked account to get.
            Note: linked_account_id is different from the linked_account_owner_id.
            See https://www.aci.dev/docs/core-concepts/linked-account#what-is-linked-account-owner-id

        Returns:
            LinkedAccountWithCredentials: The linked account including credentials if it is oauth2 account.

        Raises:
            Various exceptions defined in _handle_response for different HTTP status codes.
        """
        logger.info(f"Getting linked account with linked_account_id: {linked_account_id}")
        response = self._httpx_client.get(f"linked-accounts/{linked_account_id}")
        data: dict = self._handle_response(response)
        linked_account = LinkedAccountWithCredentials.model_validate(data)

        return linked_account

    @retry(**retry_config)  # type: ignore
    def link(
        self,
        app_name: str,
        security_scheme: SecurityScheme,
        linked_account_owner_id: str,
        api_key: str | None = None,
        after_oauth2_link_redirect_url: str | None = DEFAULT_AFTER_OAUTH2_FLOW_REDIRECT_URL,
    ) -> LinkedAccount | str:
        """Link an account with the specified authentication type.

        Args:
            app_name: Name of the app to link account for, e.g., "GMAIL"
            linked_account_owner_id: ID of the owner of the linked account, e.g., "johndoe"
            security_scheme: The security scheme to use for the linked account.
            api_key: API key for authentication (required when security_scheme is API_KEY).
            after_oauth2_link_redirect_url (Only applicable when security_scheme is OAUTH2):
                The URL to redirect to after the OAuth2 link, default to aci.dev's dev portal.

        Returns:
            if security_scheme is API_KEY or NO_AUTH, returns the linked account.
            if security_scheme is OAUTH2, returns the OAuth2 authorization URL.

        Raises:
            ValueError: If required parameters for the specified security scheme are missing.
            Various exceptions defined in _handle_response for different HTTP status codes.
        """
        response: Response | None = None

        if security_scheme == SecurityScheme.API_KEY:
            if not api_key:
                raise ValueError("api_key parameter is required when security_scheme is API_KEY")
            validated_params = LinkedAccountAPIKeyCreate(
                app_name=app_name,
                linked_account_owner_id=linked_account_owner_id,
                api_key=api_key,
            ).model_dump(exclude_none=True, mode="json")

            logger.info(
                f"Creating linked account with API key for app: {app_name}, owner_id: {linked_account_owner_id}"
            )

            response = self._httpx_client.post("linked-accounts/api-key", json=validated_params)

            return LinkedAccount.model_validate(self._handle_response(response))

        elif security_scheme == SecurityScheme.NO_AUTH:
            validated_params = LinkedAccountNoAuthCreate(
                app_name=app_name,
                linked_account_owner_id=linked_account_owner_id,
            ).model_dump(exclude_none=True, mode="json")

            logger.info(
                f"Creating linked account with no auth for app: {app_name}, owner_id: {linked_account_owner_id}"
            )

            response = self._httpx_client.post("linked-accounts/no-auth", json=validated_params)

            return LinkedAccount.model_validate(self._handle_response(response))

        elif security_scheme == SecurityScheme.OAUTH2:
            validated_params = LinkedAccountOAuth2Create(
                app_name=app_name,
                linked_account_owner_id=linked_account_owner_id,
                after_oauth2_link_redirect_url=after_oauth2_link_redirect_url,
            ).model_dump(exclude_none=True, mode="json")

            logger.info(
                f"Creating linked account with OAuth2 for app: {app_name}, owner_id: {linked_account_owner_id}"
            )

            response = self._httpx_client.get("linked-accounts/oauth2", params=validated_params)
            response_data: dict[str, str] = self._handle_response(response)

            return response_data["url"]

    @retry(**retry_config)  # type: ignore
    def delete(self, linked_account_id: UUID) -> None:
        """Delete a linked account.

        Args:
            linked_account_id: ID of the linked account to delete.

        Raises:
            Various exceptions defined in _handle_response for different HTTP status codes.
        """
        logger.info(f"Deleting linked account with ID: {linked_account_id}")
        response = self._httpx_client.delete(f"linked-accounts/{linked_account_id}")
        self._handle_response(response)

    @retry(**retry_config)  # type: ignore
    def disable(self, linked_account_id: UUID) -> LinkedAccount:
        """Disable a linked account.

        Args:
            linked_account_id: ID of the linked account to disable.

        Returns:
            LinkedAccount: The updated linked account.

        Raises:
            Various exceptions defined in _handle_response for different HTTP status codes.
        """
        return self._update(linked_account_id, enabled=False)

    @retry(**retry_config)  # type: ignore
    def enable(self, linked_account_id: UUID) -> LinkedAccount:
        """Enable a linked account.

        Args:
            linked_account_id: ID of the linked account to enable.

        Returns:
            LinkedAccount: The updated linked account.

        Raises:
            Various exceptions defined in _handle_response for different HTTP status codes.
        """
        return self._update(linked_account_id, enabled=True)

    def _update(self, linked_account_id: UUID, enabled: bool | None = None) -> LinkedAccount:
        """Update a linked account.

        Args:
            linked_account_id: ID of the linked account to update.
            enabled: whether to enable or disable the linked account.

        Returns:
            LinkedAccount: The updated linked account.

        Raises:
            Various exceptions defined in _handle_response for different HTTP status codes.
        """
        validated_params = LinkedAccountUpdate(
            enabled=enabled,
        ).model_dump(exclude_none=True, mode="json")

        logger.info(f"Updating linked account with ID: {linked_account_id}")
        response = self._httpx_client.patch(
            f"linked-accounts/{linked_account_id}",
            json=validated_params,
        )
        data: dict = self._handle_response(response)

        return LinkedAccount.model_validate(data)
