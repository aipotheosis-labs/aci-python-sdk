from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from aci.types.enums import SecurityScheme


class AppConfiguration(BaseModel):
    """Public representation of an app configuration."""

    id: UUID
    project_id: UUID
    app_name: str
    security_scheme: SecurityScheme
    enabled: bool
    all_functions_enabled: bool
    enabled_functions: list[str]
    created_at: datetime
    updated_at: datetime

    # allow extra fields for backward compatibility
    model_config = ConfigDict(extra="allow")


class AppConfigurationCreate(BaseModel):
    """Create a new app configuration.

    "all_functions_enabled=True" → ignore enabled_functions.
    "all_functions_enabled=False" AND non-empty enabled_functions → selectively enable that list.
    "all_functions_enabled=False" AND empty enabled_functions → all functions disabled.
    """

    app_name: str
    security_scheme: SecurityScheme
    security_scheme_overrides: dict | None = None
    all_functions_enabled: bool = True
    enabled_functions: list[str] | None = None


# TODO: add limit and offset boundaries
class AppConfigurationsList(BaseModel):
    app_names: list[str] | None = None
    limit: int | None = None
    offset: int | None = None
