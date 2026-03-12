"""Adds config flow for OpenMotics."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any

from pyhaopenmotics import (
    AuthenticationError,
    Installation,
    LocalGateway,
    OpenMoticsCloud,
    OpenMoticsConnectionError,
    OpenMoticsConnectionSslError,
    OpenMoticsConnectionTimeoutError,
)
import voluptuous as vol

from homeassistant.const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_IP_ADDRESS,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_VERIFY_SSL,
)
from homeassistant.helpers import config_entry_oauth2_flow, config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util.ssl import get_default_context, get_default_no_verify_context

from .const import CONF_INSTALLATION_ID, DOMAIN
from .oauth_impl import OpenMoticsOauth2Implementation

if TYPE_CHECKING:
    from collections.abc import Mapping

    from homeassistant.config_entries import ConfigFlowResult

DEFAULT_PORT = 443
DEFAULT_VERIFY_SSL = True

CLOUD_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CLIENT_ID): cv.string,
        vol.Required(CONF_CLIENT_SECRET): cv.string,
    },
)

LOCAL_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_IP_ADDRESS): cv.string,
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): bool,
    },
)
_LOGGER = logging.getLogger(__name__)


# @config_entries.HANDLERS.register(DOMAIN)
class OpenMoticsFlowHandler(config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN):
    """Handle a config flow for OpenMotics."""

    VERSION = 2
    DOMAIN = DOMAIN

    installations: list[Installation] = []
    data: dict[str, Any] = {}
    token: dict[str, Any] = {}

    def __init__(self) -> None:
        """Create a new instance of the flow handler."""
        super().__init__()

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return logging.getLogger(__name__)

    @staticmethod
    def construct_unique_id(om_type: str, install_id: str) -> str:
        """Construct the unique id from the ssdp discovery or user_step."""
        return f"{om_type}-{install_id}"

    async def _validate_local_connection(
        self,
        localgw: str,
        username: str,
        password: str,
        port: int = DEFAULT_PORT,
        verify_ssl: bool = DEFAULT_VERIFY_SSL,
    ) -> dict[str, str]:
        """Validate local connection."""
        errors: dict[str, str] = {}
        ssl_context = get_default_context()
        if not verify_ssl:
            ssl_context = get_default_no_verify_context()

        try:
            omclient = LocalGateway(
                localgw=localgw,
                username=username,
                password=password,
                port=port,
                ssl_context=ssl_context,
            )
            await omclient.get_token()

            version = await omclient.exec_action("get_version")
            _LOGGER.debug(version)
            await omclient.close()

        except OpenMoticsConnectionTimeoutError:
            errors["base"] = "cannot_connect"
        except OpenMoticsConnectionSslError:
            errors["base"] = "cannot_connect"
        except AuthenticationError:
            errors["base"] = "invalid_auth"
        except OpenMoticsConnectionError:
            errors["base"] = "cannot_connect"
        except Exception:
            _LOGGER.exception("Unexpected error during login")
            errors["base"] = "unknown"

        return errors

    async def _get_cloud_token(
        self, client_id: str, client_secret: str
    ) -> tuple[dict[str, str], dict[str, Any] | None]:
        """Get cloud token."""
        errors: dict[str, str] = {}
        token = None
        try:
            flow_impl = OpenMoticsOauth2Implementation(
                self.hass,
                domain=f"{DOMAIN}-config_flow",
                client_id=client_id,
                client_secret=client_secret,
                name=f"{DOMAIN}-config_flow",
            )
            token = await flow_impl.async_resolve_external_data(None)

        except OpenMoticsConnectionTimeoutError:
            errors["base"] = "cannot_connect"
        except OpenMoticsConnectionSslError:
            errors["base"] = "cannot_connect"
        except AuthenticationError:
            errors["base"] = "invalid_auth"
        except OpenMoticsConnectionError:
            errors["base"] = "cannot_connect"
        except Exception:
            _LOGGER.exception("Unexpected error during login")
            errors["base"] = "unknown"

        return errors, token

    def is_local_device_already_added(self) -> bool:
        """Check if a Local device has already been added."""
        for entry in self._async_current_entries():
            if entry.unique_id is not None and entry.unique_id.startswith(
                f"{DOMAIN}-local-",
            ):
                return True
        return False

    async def async_step_user(
        self,
        user_input: dict[str, str] | None = None,
    ) -> ConfigFlowResult:
        """Handle a flow initiated by the user."""
        # If there is a Local entry already, abort a new entry
        # If you want to manage multiple devices, do it via cloud
        if self.is_local_device_already_added():
            return self.async_abort(reason="already_configured_local_device")

        return await self.async_step_environment()

    async def async_step_environment(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Decide environment, cloud or local."""
        if user_input is None:
            return self.async_show_form(
                step_id="environment",
                data_schema=vol.Schema(
                    {
                        vol.Required("environment", default="cloud"): vol.In(
                            ["cloud", "local"],
                        ),
                    },
                ),
                errors={},
            )

        # Environment chosen, request additional host information for LOCAL
        # or OAuth2 flow for CLOUD
        # Ask for host detail
        if user_input["environment"] == "local":
            return await self.async_step_local()

        # Ask for cloud detail
        return await self.async_step_cloud()

    async def async_step_cloud(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle cloud flow."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self.data = {
                CONF_CLIENT_ID: user_input[CONF_CLIENT_ID],
                CONF_CLIENT_SECRET: user_input[CONF_CLIENT_SECRET],
            }

            errors, token = await self._get_cloud_token(self.data[CONF_CLIENT_ID], self.data[CONF_CLIENT_SECRET])

            if token:
                # Force int for non-compliant oauth2 providers
                try:
                    token["expires_in"] = int(token["expires_in"])
                except ValueError as err:
                    _LOGGER.warning("Error converting expires_in to int: %s", err)
                    return self.async_abort(reason="oauth_error")
                token["expires_at"] = time.time() + token["expires_in"]

                self.logger.info("Successfully authenticated")

                omclient = OpenMoticsCloud(
                    token=token["access_token"],
                    session=async_get_clientsession(self.hass),
                )

                self.installations = await omclient.installations.get_all()

                self.data["token"] = token

                if len(self.installations) > 0:
                    # show selection form
                    return await self.async_step_installation()

                errors["base"] = "discovery_error"

        return self.async_show_form(
            step_id="cloud",
            data_schema=CLOUD_SCHEMA,
            errors=errors,
        )

    async def async_step_installation(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Ask user to select the Installation ID to use."""
        if user_input is None or CONF_INSTALLATION_ID not in user_input:
            existing_installations = [
                entry.data[CONF_INSTALLATION_ID]
                for entry in self._async_current_entries()
                if CONF_INSTALLATION_ID in entry.data
            ]

            installations_options = {
                installation.idx: installation.name
                for installation in self.installations
                if installation.idx not in existing_installations
            }
            if not installations_options:
                return self.async_abort(reason="no_available_installation")

            return self.async_show_form(
                step_id="installation",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_INSTALLATION_ID): vol.In(
                            installations_options,
                        ),
                    },
                ),
            )

        self.data[CONF_INSTALLATION_ID] = user_input[CONF_INSTALLATION_ID]
        _LOGGER.debug(self.data[CONF_INSTALLATION_ID])
        return await self.async_step_create_cloudentry()

    async def async_step_create_cloudentry(self) -> ConfigFlowResult:
        """Create a config entry at completion of a flow and authorization."""
        unique_id = self.construct_unique_id(
            "openmotics-clouddev",
            self.data[CONF_INSTALLATION_ID],
        )
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        self.data["auth_implementation"] = f"{DOMAIN}-clouddev-{self.data[CONF_INSTALLATION_ID]}"

        return self.async_create_entry(title=unique_id, data=self.data)

    async def async_step_local(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle local flow."""
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = await self._validate_local_connection(
                user_input[CONF_IP_ADDRESS],
                username=user_input[CONF_NAME],
                password=user_input[CONF_PASSWORD],
                port=user_input.get(CONF_PORT, DEFAULT_PORT),
                verify_ssl=user_input.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
            )

            if not errors:
                self.data = user_input
                unique_id = self.construct_unique_id(
                    "openmotics-local",
                    self.data[CONF_IP_ADDRESS],
                )
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=unique_id, data=self.data)

        return self.async_show_form(
            step_id="local",
            data_schema=LOCAL_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> ConfigFlowResult:
        """Handle re-authentication with OpenMotics."""
        # self.entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])

        if CONF_IP_ADDRESS in entry_data:
            # self.data = entry_data
            return await self.async_step_reauth_local_confirm()

        return await self.async_step_reauth_cloud_confirm()

    async def async_step_reauth_local_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle local re-authentication."""
        errors: dict[str, str] = {}

        if user_input is not None:
            reauth_entry = self._get_reauth_entry()
            errors = await self._validate_local_connection(
                localgw=reauth_entry.data[CONF_IP_ADDRESS],
                username=user_input[CONF_NAME],
                password=user_input[CONF_PASSWORD],
                port=reauth_entry.data[CONF_PORT],
                verify_ssl=reauth_entry.data[CONF_VERIFY_SSL],
            )

            if not errors:
                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data_updates={
                        CONF_NAME: user_input[CONF_NAME],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                    },
                )

        return self.async_show_form(
            step_id="reauth_local_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME): cv.string,
                    vol.Required(CONF_PASSWORD): cv.string,
                }
            ),
            errors=errors,
        )

    async def async_step_reauth_cloud_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle cloud re-authentication."""
        errors: dict[str, str] = {}

        if user_input is not None:
            reauth_entry = self._get_reauth_entry()
            errors, token = await self._get_cloud_token(user_input[CONF_CLIENT_ID], user_input[CONF_CLIENT_SECRET])

            if not errors and token is not None:
                # Force int for non-compliant oauth2 providers
                try:
                    token["expires_in"] = int(token["expires_in"])
                except ValueError as err:
                    _LOGGER.warning("Error converting expires_in to int: %s", err)
                    return self.async_abort(reason="oauth_error")
                token["expires_at"] = time.time() + token["expires_in"]

                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data_updates={
                        CONF_CLIENT_ID: user_input[CONF_CLIENT_ID],
                        CONF_CLIENT_SECRET: user_input[CONF_CLIENT_SECRET],
                        "token": token,
                    },
                )

        return self.async_show_form(
            step_id="reauth_cloud_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_CLIENT_ID): cv.string,
                    vol.Required(CONF_CLIENT_SECRET): cv.string,
                }
            ),
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle reconfiguration of an entry."""
        entry = self._get_reconfigure_entry()

        if CONF_IP_ADDRESS in entry.data:
            return await self.async_step_reconfigure_local(user_input)

        return await self.async_step_reconfigure_cloud(user_input)

    async def async_step_reconfigure_local(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle local reconfiguration."""
        errors = {}
        entry = self._get_reconfigure_entry()

        if user_input is not None:
            errors = await self._validate_local_connection(
                localgw=user_input[CONF_IP_ADDRESS],
                username=user_input[CONF_NAME],
                password=user_input[CONF_PASSWORD],
                port=user_input.get(CONF_PORT, DEFAULT_PORT),
                verify_ssl=user_input.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
            )

            if not errors:
                return self.async_update_reload_and_abort(
                    entry,
                    data={**entry.data, **user_input},
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_IP_ADDRESS, default=entry.data[CONF_IP_ADDRESS]): cv.string,
                vol.Required(CONF_NAME, default=entry.data[CONF_NAME]): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Optional(CONF_PORT, default=entry.data.get(CONF_PORT, DEFAULT_PORT)): int,
                vol.Optional(
                    CONF_VERIFY_SSL,
                    default=entry.data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
                ): bool,
            }
        )

        return self.async_show_form(
            step_id="reconfigure_local",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_reconfigure_cloud(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle cloud reconfiguration."""
        errors: dict[str, str] = {}
        entry = self._get_reconfigure_entry()

        if user_input is not None:
            errors, token = await self._get_cloud_token(user_input[CONF_CLIENT_ID], user_input[CONF_CLIENT_SECRET])

            if not errors and token is not None:
                return self.async_update_reload_and_abort(
                    entry,
                    data={**entry.data, **user_input},
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_CLIENT_ID, default=entry.data.get(CONF_CLIENT_ID)): cv.string,
                vol.Required(CONF_CLIENT_SECRET, default=entry.data.get(CONF_CLIENT_SECRET)): cv.string,
            }
        )

        return self.async_show_form(
            step_id="reconfigure_cloud",
            data_schema=schema,
            errors=errors,
        )
