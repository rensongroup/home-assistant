"""Local implementation of OAuth2.

Local implementation of OAuth2 specific to OpenMotics to
hard code client id and secret and return a proper name.
"""

from __future__ import annotations

import logging
from typing import Any
import uuid

from pyhaopenmotics.const import (
    CLOUD_SCOPE,
    OAUTH2_AUTHORIZE,
    OAUTH2_TOKEN,
    OLD_CLOUD_SCOPE,
    OLD_OAUTH2_AUTHORIZE,
    OLD_OAUTH2_TOKEN,
)

from homeassistant.core import HomeAssistant
from homeassistant.helpers.config_entry_oauth2_flow import LocalOAuth2Implementation

_LOGGER = logging.getLogger(__name__)


# To be removed in the future
def is_valid_uuid(uuid_to_test: str, version: int = 4) -> bool:
    """Check if uuid_to_test is a valid UUID."""
    try:
        # check for validity of Uuid
        uuid_obj = uuid.UUID(uuid_to_test, version=version)
        if uuid_obj:
            pass
    except ValueError:
        return False
    return True


class OpenMoticsOauth2Implementation(LocalOAuth2Implementation):
    """Local implementation of OAuth2."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        hass: HomeAssistant,
        domain: str,
        client_id: str,
        client_secret: str,
        name: str,
    ) -> None:
        """Local Toon Oauth Implementation."""
        self._name = name
        self._my_cloud_scope: str

        # To be removed in the future
        if is_valid_uuid(client_id):
            _my_authorize_url = OAUTH2_AUTHORIZE
            _my_token_url = OAUTH2_TOKEN
            self._my_cloud_scope = CLOUD_SCOPE
        else:
            _my_authorize_url = OLD_OAUTH2_AUTHORIZE
            _my_token_url = OLD_OAUTH2_TOKEN
            self._my_cloud_scope = OLD_CLOUD_SCOPE
            _LOGGER.warning(
                "Client ID is not a valid UUID, using old OAuth2 endpoints. Please check documentation.",
            )
        """Just init default class with default values."""
        super().__init__(
            hass=hass,
            domain=domain,
            client_id=client_id,
            client_secret=client_secret,
            authorize_url=_my_authorize_url,
            token_url=_my_token_url,
        )
        _LOGGER.debug("Init OpenMoticsOauth2Implementation: %s", self.name)

    @property
    def name(self) -> str:
        """Name of the implementation."""
        return self._name

    # @property
    # def extra_token_resolve_data(self) -> dict:
    #     """Extra data that needs to be appended to the authorize url."""
    #     # Overruling config_entry_oauth2_flow.
    #     data: dict = {"scope": self._my_cloud_scope}
    #     return data

    # @property
    # def extra_authorize_data(self) -> dict[str, Any]:
    #     """Extra data that needs to be appended to the authorize url."""
    #     # Overruling config_entry_oauth2_flow.
    #     data: dict = {"scope": self.cloud_scope}
    #     data.update(super().extra_authorize_data)
    #     return data

    async def async_resolve_external_data(self, external_data: Any) -> dict:
        """Resolve the authorization code to tokens."""
        # Overruling config_entry_oauth2_flow.
        data: dict = {
            "grant_type": "client_credentials",
            "scope": self._my_cloud_scope,
        }
        return await self._token_request(data)

    async def _async_refresh_token(self, token: dict) -> dict:
        """Refresh tokens."""
        # Overruling config_entry_oauth2_flow.
        _LOGGER.debug("Refreshing token of %s", self.name)
        data: dict = {
            "grant_type": "client_credentials",
            # "client_id": self.client_id,
            # "refresh_token": token["refresh_token"],
            "scope": self._my_cloud_scope,
        }
        _LOGGER.debug("data: %s", data)
        new_token = await self._token_request(data)

        return {**token, **new_token}
