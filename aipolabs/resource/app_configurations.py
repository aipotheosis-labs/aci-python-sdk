import logging
from typing import List

from tenacity import retry

from aipolabs.resource._base import APIResource, retry_config
from aipolabs.types.app_configurations import (
    AppConfigurationCreate,
    AppConfigurationPublic,
    AppConfigurationsList,
)
from aipolabs.types.enums import SecurityScheme

logger: logging.Logger = logging.getLogger(__name__)


class AppConfigurationsResource(APIResource):
    """Resource for managing app configurations."""

    @retry(**retry_config)
    def list(
        self,
        app_names: list[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> List[AppConfigurationPublic]:
        """List app configurations.

        Args:
            app_names: Filter by app names.
            limit: Maximum number of results per response.
            offset: Pagination offset.

        Returns:
            List[AppConfigurationPublic]: List of app configurations.

        Raises:
            Various exceptions defined in _handle_response for different HTTP status codes.
        """
        validated_params = AppConfigurationsList(
            app_names=app_names,
            limit=limit,
            offset=offset,
        ).model_dump(exclude_none=True, mode="json")

        logger.info(f"Listing app configurations with params: {validated_params}")
        response = self._httpx_client.get(
            "app-configurations",
            params=validated_params,
        )

        data: List[dict] = self._handle_response(response)
        app_configurations = [AppConfigurationPublic.model_validate(config) for config in data]
        return app_configurations

    @retry(**retry_config)
    def get(self, app_name: str) -> AppConfigurationPublic:
        """Get an app configuration by app name.

        Args:
            app_name: Name of the app to get configuration for.

        Returns:
            AppConfigurationPublic: The app configuration.

        Raises:
            Various exceptions defined in _handle_response for different HTTP status codes.
        """
        logger.info(f"Getting app configuration for app: {app_name}")
        response = self._httpx_client.get(f"app-configurations/{app_name}")
        data: dict = self._handle_response(response)
        app_configuration = AppConfigurationPublic.model_validate(data)

        return app_configuration  # type: ignore

    @retry(**retry_config)
    def create(
        self,
        app_name: str,
        security_scheme: SecurityScheme,
    ) -> AppConfigurationPublic:
        """Create an app configuration.

        Args:
            app_name: Unique name of the app to create configuration for.
            security_scheme: Security scheme to use for the app configuration.

        Returns:
            AppConfigurationPublic: The created app configuration.

        Raises:
            Various exceptions defined in _handle_response for different HTTP status codes.
        """
        # TODO: add support for security_scheme_overrides, all_functions_enabled, enabled_functions
        validated_params = AppConfigurationCreate(
            app_name=app_name,
            security_scheme=security_scheme,
            security_scheme_overrides=None,
            all_functions_enabled=True,
            enabled_functions=None,
        ).model_dump(exclude_none=True, mode="json")

        logger.info(f"Creating app configuration: {validated_params}")

        response = self._httpx_client.post(
            "app-configurations",
            json=validated_params,
        )
        data: dict = self._handle_response(response)

        return AppConfigurationPublic.model_validate(data)  # type: ignore

    @retry(**retry_config)
    def delete(self, app_name: str) -> None:
        """Delete an app configuration.

        Args:
            app_name: Name of the app to delete configuration for.

        Raises:
            Various exceptions defined in _handle_response for different HTTP status codes.
        """
        logger.info(f"Deleting app configuration for app: {app_name}")
        response = self._httpx_client.delete(f"app-configurations/{app_name}")
        self._handle_response(response)

    # TODO: update are not supported for now
