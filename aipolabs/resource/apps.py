import logging

from tenacity import retry

from aipolabs.resource._base import APIResource, retry_config
from aipolabs.types._apps import App, SearchAppsParams

logger: logging.Logger = logging.getLogger(__name__)


class AppsResource(APIResource):

    @retry(**retry_config)
    def search(
        self, intent: str | None = None, limit: int | None = None, offset: int | None = None
    ) -> list[App]:
        """Searches for apps using the provided parameters.

        Args:
            intent: search results will be sorted by relevance to this intent.
            limit: for pagination, maximum number of apps to return.
            offset: for pagination, number of apps to skip before returning results.

        Returns:
            list[AipolabsSearchApps.App]: List of apps matching the search criteria in the order of relevance.

        Raises:
            Various exceptions defined in _handle_response for different HTTP status codes.
        """
        validated_params = SearchAppsParams(intent=intent, limit=limit, offset=offset).model_dump(
            exclude_none=True
        )

        logger.info(f"Searching apps with params: {validated_params}")
        response = self._httpx_client.get(
            "apps/search",
            params=validated_params,
        )

        data: list[dict] = self._handle_response(response)
        apps = [App.model_validate(app) for app in data]

        return apps
