"""DataUpdateCoordinator for the OpenMotics integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import TYPE_CHECKING, Any

from pyhaopenmotics import (
    LocalGateway,
    OpenMoticsCloud,
    OpenMoticsConnectionError,
    OpenMoticsConnectionSslError,
    OpenMoticsConnectionTimeoutError,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_IP_ADDRESS,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_VERIFY_SSL,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util.ssl import get_default_context, get_default_no_verify_context

from .const import CONF_INSTALLATION_ID, DEFAULT_SCAN_INTERVAL, DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.config_entry_oauth2_flow import OAuth2Session

UPDATE_INTERVAL = timedelta(seconds=30)

_LOGGER = logging.getLogger(__name__)

type OpenMoticsCloudConfigEntry = ConfigEntry[OpenMoticsCloudDataUpdateCoordinator]
type OpenMoticsLocalConfigEntry = ConfigEntry[OpenMoticsLocalDataUpdateCoordinator]


class OpenMoticsDataUpdateCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Query OpenMotics devices and keep track of seen conditions."""

    def __init__(self, hass: HomeAssistant, *, name: str) -> None:
        """Initialize the OpenMotics gateway."""
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=name or DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        # self.session = None
        self._omclient: OpenMoticsCloud | LocalGateway
        self._install_id = None

    async def _async_update_data(self) -> dict[Any, Any]:
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        my_outputs = []
        my_lights = []
        my_groupactions = []
        my_shutters = []
        my_sensors = []
        my_thermostatgroups = []
        my_thermostatunits = []
        my_energysensors = []

        try:
            my_outputs = await self._omclient.outputs.get_all()
            my_lights = await self._omclient.lights.get_all()
            my_groupactions = await self._omclient.groupactions.get_all()
            my_shutters = await self._omclient.shutters.get_all()
            my_sensors = await self._omclient.sensors.get_all()
            my_thermostatgroups = await self._omclient.thermostats.groups.get_all()
            my_thermostatunits = await self._omclient.thermostats.units.get_all()
            my_energysensors = await self._omclient.energysensors.get_all()

        # https://developers.home-assistant.io/docs/integration_setup_failures#handling-expired-credentials
        #
        # Sometimes the connection fails because of expired credentials, but we don't want to raise an error in that case,
        # because the credentials will be refreshed automatically and the next update will succeed.
        # If we trigger ConfigEntryAuthFailed, the device will be disabled and the user will have to re-enable it.
        # At his moment, we don't know why these credentials got expired.
        #
        except (OpenMoticsConnectionTimeoutError, OpenMoticsConnectionError) as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="update_failed",
                translation_placeholders={"error": repr(err)},
            ) from err
        except OpenMoticsConnectionSslError as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="ssl_failed",
                translation_placeholders={"error": repr(err)},
            ) from err
        except Exception as err:
            _LOGGER.exception("Unexpected error during _async_update_data")
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="exception_occurred",
                translation_placeholders={"error": repr(err)},
            ) from err

        # Store data in a way Home Assistant can easily consume it
        return {
            "outputs": my_outputs,
            "lights": my_lights,
            "groupactions": my_groupactions,
            "shutters": my_shutters,
            "sensors": my_sensors,
            "energysensors": my_energysensors,
            "thermostatgroups": my_thermostatgroups,
            "thermostatunits": my_thermostatunits,
        }

    @property
    def omclient(self) -> Any:
        """Return the backendclient."""
        return self._omclient

    @property
    def install_id(self) -> Any:
        """Return the backendclient."""
        return self._install_id


class OpenMoticsCloudDataUpdateCoordinator(OpenMoticsDataUpdateCoordinator):
    """Query OpenMotics devices and keep track of seen conditions."""

    config_entry: OpenMoticsCloudConfigEntry

    def __init__(self, hass: HomeAssistant, session: OAuth2Session, name: str) -> None:
        """Initialize the OpenMotics gateway."""
        super().__init__(
            hass=hass,
            name=name,
        )
        self.session = session
        self._install_id = self.config_entry.data.get(CONF_INSTALLATION_ID)  # type: ignore

        async def async_token_refresh() -> Any:
            """Token_refresh_method for OpenMoticsCloud."""
            await session.async_ensure_token_valid()
            return session.token["access_token"]

        client_session = async_get_clientsession(hass)

        self._omclient = OpenMoticsCloud(
            token=session.token["access_token"],
            session=client_session,
            token_refresh_method=async_token_refresh,
        )

    async def _async_update_data(self) -> dict[Any, Any]:
        """Fetch data from API endpoint."""
        await self.session.async_ensure_token_valid()
        return await super()._async_update_data()


class OpenMoticsLocalDataUpdateCoordinator(OpenMoticsDataUpdateCoordinator):
    """Query OpenMotics devices and keep track of seen conditions."""

    config_entry: OpenMoticsLocalConfigEntry

    def __init__(self, hass: HomeAssistant, name: str) -> None:
        """Initialize the OpenMotics gateway."""
        super().__init__(
            hass=hass,
            name=name,
        )
        self.session = async_get_clientsession(hass)

        self._install_id = self.config_entry.data.get(CONF_IP_ADDRESS)  # type: ignore
        ssl_context = get_default_context()
        if not self.config_entry.data.get(CONF_VERIFY_SSL):
            ssl_context = get_default_no_verify_context()

        """Set up a OpenMotics controller"""
        self._omclient = LocalGateway(
            localgw=self.config_entry.data.get(CONF_IP_ADDRESS),  # type: ignore
            username=self.config_entry.data.get(CONF_NAME),  # type: ignore
            password=self.config_entry.data.get(CONF_PASSWORD),  # type: ignore
            port=self.config_entry.data.get(CONF_PORT),  # type: ignore
            ssl_context=ssl_context,
            session=self.session,
        )
