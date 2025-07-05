from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from aci.types.enums import SecurityScheme


class LinkedAccountCreateBase(BaseModel):
    """Base model for creating a linked account."""

    app_name: str
    linked_account_owner_id: str


class LinkedAccountOAuth2Create(LinkedAccountCreateBase):
    """Model for creating an OAuth2 linked account."""

    after_oauth2_link_redirect_url: str | None = None


class LinkedAccountAPIKeyCreate(LinkedAccountCreateBase):
    """Model for creating an API key linked account."""

    api_key: str


class LinkedAccountNoAuthCreate(LinkedAccountCreateBase):
    """Model for creating a no-auth linked account."""

    pass


class LinkedAccountUpdate(BaseModel):
    """Model for updating a linked account."""

    enabled: bool | None = None


class OAuth2SchemeCredentialsLimited(BaseModel):
    """Limited OAuth2 credentials containing only access token"""

    access_token: str
    expires_at: int | None = None  # access token expiration time, seconds since epoch
    refresh_token: str | None = None  # refresh token, if present


class LinkedAccount(BaseModel):
    """Public representation of a linked account."""

    id: UUID
    project_id: UUID
    app_name: str
    linked_account_owner_id: str
    security_scheme: SecurityScheme
    enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="allow")


class LinkedAccountWithCredentials(LinkedAccount):
    """Linked account with credentials (only OAuth2 is supported for now)"""

    security_credentials: OAuth2SchemeCredentialsLimited | None = None

    # if security_credentials is empty dict (which is the case for API key and no-auth accounts), set it to None
    @field_validator("security_credentials", mode="before")
    def validate_security_credentials(cls, v: dict) -> dict | None:
        if not v:
            return None
        return v


class LinkedAccountsList(BaseModel):
    """Parameters for listing linked accounts."""

    app_name: str | None = None
    linked_account_owner_id: str | None = None
