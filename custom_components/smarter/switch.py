"""Support for Smarter sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .smarter_client.managed_devices.base import BaseDevice

from .const import DOMAIN
from .entity import SmarterEntity


def make_check_status(key: str, values: list[Any]) -> bool:
    """Return a function that checks the status of a device."""

    def _check_status(device: BaseDevice) -> bool:
        return device.device.status.get(key) in values

    return _check_status


def set_boil(device: BaseDevice, value: bool):
    """Invoke or cancel the boil command."""
    device.send_command("start_boil" if value else "stop_boil", True)


@dataclass(frozen=True, kw_only=True)
class SmarterSwitchEntityDescription(SwitchEntityDescription):
    """Represent the Smarter sensor entity description."""

    get_fn: Callable[[BaseDevice], bool]
    set_fn: Callable[[BaseDevice, Any], None]


SWITCH_TYPES = [
    SmarterSwitchEntityDescription(
        key="start_boil",
        name="Boiling",
        get_fn=make_check_status("state", ["Boiling", "Keeping Warm", "Cooling"]),
        set_fn=set_boil,
        icon="mdi:kettle-steam",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smarter sensors."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    entities = [
        SmarterSwitch(device, description)
        for device in data.get("devices")
        for description in SWITCH_TYPES
    ]

    async_add_entities(entities, True)


class SmarterSwitch(SmarterEntity, SwitchEntity):
    """Representation of a Smarter binary sensor."""

    entity_description: SmarterSwitchEntityDescription

    _attr_has_entity_name = True

    @property
    def is_on(self) -> bool | None:
        """Return the state of the sensor."""
        return self.entity_description.get_fn(self.device)

    def turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        self.entity_description.set_fn(self.device, True)
        self._attr_is_on = True

    def turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        self.entity_description.set_fn(self.device, False)
        self._attr_is_on = False
