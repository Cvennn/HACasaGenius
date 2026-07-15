"""
Switch platform for swegon_genius.

Switch entities:
1. CO2 Automation - register 4x5009 (0=off 1=on)
2. Fireplace - register 4x5002 (0=off 1=on)
3. Cooking mode - register 4x5005 (0=off 1=on)
4. RH Control (Sorption units only) - register 4x5224 (0=off 1=on) — SCB 4.2

    WARNING (per Swegon datasheet, SCB 4.2, register 4x5224):
    "Do not disable RH Control in Sorption rotor units."

Switches are on/off registers, not select entities.
Emergency stop contains a third state (2 = Emergency Overpressurizing enable),
which is not exposed by the switch. If value 2 is active, switch is set to ON.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

# Switches where turning OFF is discouraged by the Swegon datasheet.
# Currently only RH Control on Sorption rotor units (register 4x5224):
# "Do not disable RH Control in Sorption rotor units."
_WARN_ON_DISABLE = {"rh_control_sorption"}

SWITCHES = [
    {
        "key": "co2_automation",
        "translation_key": "co2_automation",
        "address": 5008,
        "read_key": "co2_automation",
    },
    {
        "key": "fireplace",
        "translation_key": "fireplace",
        "address": 5001,
        "read_key": "fireplace_active",
    },
    {
        "key": "cooking_mode",
        "translation_key": "cooking_mode",
        "address": 5004,
        "read_key": "cooking_active",
    },
    {
        "key": "rh_control_sorption",
        "translation_key": "rh_control_sorption",
        "address": 5223,
        "read_key": "rh_control_sorption",
    },
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Swegon switch entities from a config entry."""
    coordinator = entry.runtime_data
    async_add_entities([SwegonSwitch(coordinator, entry, s) for s in SWITCHES])


class SwegonSwitch(CoordinatorEntity, SwitchEntity):
    """Swegon Genius switch entity."""

    def __init__(self, coordinator: Any, entry: ConfigEntry, switch_def: dict) -> None:
        """
        Initialize the switch.

        Parameters
        ----------
        coordinator : Any
            The coordinator for the device.
        entry : ConfigEntry
            The config entry for the device.
        switch_def : dict
            The switch definition dictionary.

        """
        super().__init__(coordinator)
        self._switch = switch_def
        self._attr_unique_id = f"{entry.entry_id}_{switch_def['key']}"
        self._attr_has_entity_name = True
        self._attr_translation_key = self._switch["translation_key"]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Swegon",
            model=coordinator.device_info_data.get("model", "CASA Genius"),
            sw_version=coordinator.device_info_data.get("firmware"),
        )

    @property
    def is_on(self) -> bool:
        """
        Return True if the switch is on.

        Returns
        -------
        bool
            True if the switch is on, False otherwise.

        """
        val = self.coordinator.data.get(self._switch["read_key"])
        return bool(val) if val is not None else False

    async def async_turn_on(self) -> None:
        """Turn on the switch."""
        await self.coordinator.client.write_register(self._switch["address"], 1)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn off the switch."""
        if self._switch["key"] in _WARN_ON_DISABLE:
            _LOGGER.warning(
                "Disabling '%s' is not recommended by Swegon on Sorption "
                "rotor units. Only disable it if you are certain your "
                "unit does not have a Sorption rotor, or during "
                "commissioning",
                self._switch["translation_key"],
            )
        await self.coordinator.client.write_register(self._switch["address"], 0)
        await self.coordinator.async_request_refresh()
