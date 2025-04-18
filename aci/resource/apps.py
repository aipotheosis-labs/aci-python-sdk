import logging

from tenacity import retry

from aci.resource._base import APIResource, retry_config
from aci.types.apps import AppBasic, AppDetails, SearchAppsParams

logger: logging.Logger = logging.getLogger(__name__)


class AppsResource(APIResource):
    @retry(**retry_config)  # type: ignore
    def search(
        self,
        intent: str | None = None,
        allowed_apps_only: bool = False,
        include_functions: bool = False,
        categories: list[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[AppBasic]:
        """Search for apps.

        Args:
            intent: search results will be sorted by relevance to this intent.
            allowed_apps_only: If true, only return apps that are allowed by the agent/accessor, identified by the api key.
            include_functions: If true, include functions (name and description) in the search results.
            categories: list of categories to filter apps by.
            limit: for pagination, maximum number of apps to return.
            offset: for pagination, number of apps to skip before returning results.

        Returns:
            list[AppBasic]: List of apps matching the search criteria in the order of relevance.

        Raises:
            Various exceptions defined in _handle_response for different HTTP status codes.
        """
        validated_params = SearchAppsParams(
            intent=intent,
            allowed_apps_only=allowed_apps_only,
            include_functions=include_functions,
            categories=categories,
            limit=limit,
            offset=offset,
        ).model_dump(exclude_none=True, mode="json")

        logger.info(f"Searching apps with params: {validated_params}")
        response = self._httpx_client.get(
            "apps/search",
            params=validated_params,
        )

        data: list[dict] = self._handle_response(response)
        apps = [AppBasic.model_validate(app) for app in data]

        return apps

    @retry(**retry_config)  # type: ignore
    def get(self, app_name: str) -> AppDetails:
        """Gets detailed information about an app."""
        response = self._httpx_client.get(f"apps/{app_name}")
        data: dict = self._handle_response(response)
        app_details: AppDetails = AppDetails.model_validate(data)
        return app_details
