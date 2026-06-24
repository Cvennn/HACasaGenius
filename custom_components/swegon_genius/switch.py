"""
Switch platform for swegon_genius.

Two switch entities:
1. CO2 Automation - register 4x5009 (0=off 1=on)
2. Emergency stop - register 4x5018 (0=disables 1=enabled)

Switches are on/off registers, not select entities.
Emergency stop contains a third state (2 = Emergency Overpressurizing enable),
which is not exposed by the switch. If value 2 is active, switch is set to ON.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SwegonGeniusCoordinator
from .registers_genius import SWITCH_REGISTERS

_LOGGER = logging.getLogger(__name__)


@dataclass
class SwegonSwitchDescription(SwitchEntityDescription):
    """Describes Genius switch entity."""
    coordinator_key: str = ""


SWITCH_DESCRIPTIONS: list[SwegonSwitchDescription] = [
    SwegonSwitchDescription(
        key="co2_automation",
        coordinator_key="co2_automation",
        name="CO2 Automation",
        icon=SWITCH_REGISTERS["co2_automation"]["icon"],
        device_class=SwitchDeviceClass.SWITCH,
    ),
    SwegonSwitchDescription(
        key="emergency_stop",
        coordinator_key="emergency_stop",
        name="Emergency Stop",
        icon=SWITCH_REGISTERS["emergency_stop"]["icon"],
        device_class=SwitchDeviceClass.SWITCH,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Swegon GENIUS switch entities from a config entry."""
    coordinator: SwegonGeniusCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        SwegonGeniusSwitch(coordinator, entry, description)
        for description in SWITCH_DESCRIPTIONS
    )


class SwegonGeniusSwitch(CoordinatorEntity[SwegonGeniusCoordinator], SwitchEntity):
    """Switch entity for CO2 Automation and emergency stop."""

    entity_description: SwegonSwitchDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SwegonGeniusCoordinator,
        entry: ConfigEntry,
        description: SwegonSwitchDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Swegon CASA Genius",
            model="CASA Genius",
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self.entity_description.coordinator_key)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on the switch."""
        _LOGGER.debug("Turning ON switch %s", self.entity_description.key)
        await self.coordinator.async_write_switch(
            self.entity_description.coordinator_key, True
        )

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the switch."""
        _LOGGER.debug("Turning OFF switch %s", self.entity_description.key)
        await self.coordinator.async_write_switch(
            self.entity_description.coordinator_key, False
        )
