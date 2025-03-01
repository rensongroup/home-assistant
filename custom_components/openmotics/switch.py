"""Support for HomeAssistant switches."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity

from .const import DOMAIN, NOT_IN_USE
from .entity import OpenMoticsDevice

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import OpenMoticsDataUpdateCoordinator


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Switches for OpenMotics Controller."""
    entities = []

    coordinator: OpenMoticsDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    for index, om_outlet in enumerate(coordinator.data["outputs"]):
        if om_outlet.name is None or not om_outlet.name or om_outlet.name == NOT_IN_USE:
            continue

        # Outputs can contain outlets and lights, so filter out only the outlets
        # (aka switches)
        if om_outlet.output_type != "LIGHT":
            entities.append(OpenMoticsSwitch(coordinator, index, om_outlet))

    if not entities:
        _LOGGER.info("No OpenMotics Outlets added")
        return

    async_add_entities(entities)


class OpenMoticsSwitch(OpenMoticsDevice, SwitchEntity):
    """Representation of a OpenMotics switch."""

    def __init__(
        self,
        coordinator: OpenMoticsDataUpdateCoordinator,
        index: int,
        om_switch: dict[str, Any],
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, index, om_switch, "switch")

    @property
    def is_on(self) -> Any:
        """Return true if device is on."""
        try:
            self._device = self.coordinator.data["outputs"][self.index]
            return self._device.status.on
        except (AttributeError, KeyError):
            return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn device off."""
        result = await self.coordinator.omclient.outputs.turn_on(
            self.device_id,
            100,  # value is required but an outlet goes only on/off so we set it to 100
        )
        await self._update_state_from_result(result, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn device off."""
        result = await self.coordinator.omclient.outputs.turn_off(
            self.device_id,
        )
        await self._update_state_from_result(result, False)

    async def async_toggle(self, **kwargs: Any) -> None:
        """Turn device off."""
        await self.coordinator.omclient.outputs.toggle(
            self.device_id,
        )
        await self.coordinator.async_refresh()

    @property
    def icon(self) -> str | None:
        """Return the icon to use."""
        # Valve
        if self._device.output_type == "VALVE":
            if self.is_on:
                return "mdi:valve-open"
            return "mdi:valve-closed"
        # Fan / Ventilation.
        if self._device.output_type == "VENTILATION":
            if self.is_on:
                return "mdi:fan"
            return "mdi:fan-off"
        # HVAC.
        if self._device.output_type == "HVAC":
            if self.is_on:
                return "mdi:hvac"
            return "mdi:hvac-off"
        return None

    async def _update_state_from_result(self, result: Any, state: bool) -> None:
        if isinstance(result, dict) and result.get("success") is True:
            self._device.status.on = state
            self.async_write_ha_state()
        else:
            _LOGGER.debug("Invalid result, refreshing all")
            await self.coordinator.async_refresh()
