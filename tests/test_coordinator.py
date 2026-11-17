"""Test the OpenMotics data update coordinator."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from custom_components.openmotics.coordinator import OpenMoticsDataUpdateCoordinator
from pyhaopenmotics.openmoticsgw.models.energy import EnergySensor
import pytest

from homeassistant.core import HomeAssistant

ENERGY_SENSOR = EnergySensor.from_dict({"id": 0, "name": "Main", "status": [230.0, 50.0, 1.0, 230.0]})


def _coordinator(hass: HomeAssistant, get_all: AsyncMock) -> OpenMoticsDataUpdateCoordinator:
    """Return a coordinator with a mocked client whose energy sensors use `get_all`."""
    coordinator = OpenMoticsDataUpdateCoordinator(hass, name="test")
    client = MagicMock()
    client.energysensors.get_all = get_all
    coordinator._omclient = client  # noqa: SLF001
    return coordinator


async def test_energysensors_returned_when_available(hass: HomeAssistant) -> None:
    """Energy sensors are passed through when the library returns them."""
    coordinator = _coordinator(hass, AsyncMock(return_value=[ENERGY_SENSOR]))

    assert await coordinator._async_get_energysensors() == [ENERGY_SENSOR]  # noqa: SLF001


async def test_energysensors_keyerror_reuses_previous_list_without_status(
    hass: HomeAssistant, caplog: pytest.LogCaptureFixture
) -> None:
    """A `KeyError` from the library keeps the previous sensors, with their status cleared."""
    coordinator = _coordinator(hass, AsyncMock(side_effect=KeyError("2")))
    coordinator.data = {"energysensors": [ENERGY_SENSOR]}

    sensors = await coordinator._async_get_energysensors()  # noqa: SLF001
    await coordinator._async_get_energysensors()  # noqa: SLF001

    assert len(sensors) == 1
    assert sensors[0].name == "Main"
    assert sensors[0].status is None
    assert ENERGY_SENSOR.status is not None
    assert caplog.text.count("Energy sensors unavailable") == 1


async def test_energysensors_keyerror_without_previous_data(hass: HomeAssistant) -> None:
    """A `KeyError` on the first update returns an empty list instead of failing."""
    coordinator = _coordinator(hass, AsyncMock(side_effect=KeyError("2")))

    assert await coordinator._async_get_energysensors() == []  # noqa: SLF001
