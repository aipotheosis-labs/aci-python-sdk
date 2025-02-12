import logging

from tenacity import retry

from aipolabs.resource._base import APIResource, retry_config
from aipolabs.types.apps import App, AppDetails, SearchAppsParams

logger: logging.Logger = logging.getLogger(__name__)


class AppsResource(APIResource):

    @retry(**retry_config)
    def search(
        self,
        intent: str | None = None,
        configured_only: bool = False,
        categories: list[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[App]:
        """Search for apps.

        Args:
            intent: search results will be sorted by relevance to this intent.
            configured_only: if True, only apps that have been configured in the current project will be returned.
            categories: list of categories to filter apps by.
            limit: for pagination, maximum number of apps to return.
            offset: for pagination, number of apps to skip before returning results.

        Returns:
            list[App]: List of apps matching the search criteria in the order of relevance.

        Raises:
            Various exceptions defined in _handle_response for different HTTP status codes.
        """
        validated_params = SearchAppsParams(
            intent=intent,
            configured_only=configured_only,
            categories=categories,
            limit=limit,
            offset=offset,
        ).model_dump(exclude_none=True)

        logger.info(f"Searching apps with params: {validated_params}")
        response = self._httpx_client.get(
            "apps/search",
            params=validated_params,
        )

        data: list[dict] = self._handle_response(response)
        apps = [App.model_validate(app) for app in data]

        return apps

    @retry(**retry_config)
    def get(self, app_name: str) -> AppDetails:
        """Gets detailed information about an app."""
        response = self._httpx_client.get(f"apps/{app_name}")
        data: dict = self._handle_response(response)
        app_details: AppDetails = AppDetails.model_validate(data)
        return app_details
