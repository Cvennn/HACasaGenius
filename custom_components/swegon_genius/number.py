"""
Number platform for CASA Genius.

Exposes temperature setpoint as a number entity.
SCB 4.1 register 4x5101:
  Range:  130–250 (raw Modbus integer)
  Scale:  ÷10 for display  → 13.0–25.0 °C
  Step:   0.5 °C  (raw step = 5)
  Write:  °C value × 10 → integer sent to Modbus
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SwegonGeniusCoordinator
from .registers_genius import NUMBER_REGISTERS

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)


NUMBER_DESCRIPTION = NumberEntityDescription(
    key="temperature_setpoint",
    name="Temperature Setpoint",
    device_class=NumberDeviceClass.TEMPERATURE,
    mode=NumberMode.BOX,
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    native_max_value=NUMBER_REGISTERS["temperature_setpoint"]["max"],
    native_min_value=NUMBER_REGISTERS["temperature_setpoint"]["min"],
    native_step=NUMBER_REGISTERS["temperature_setpoint"]["step"],
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up number entity from a config entry."""
    coordinator: SwegonGeniusCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SwegonGeniusNumber(coordinator, entry)])


class SwegonGeniusNumber(CoordinatorEntity[SwegonGeniusCoordinator], NumberEntity):
    """Temperature setpoint entity."""

    _attr_has_entity_name = True
    entity_description = NUMBER_DESCRIPTION

    def __init__(
        self, coordinator: SwegonGeniusCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_temperature_setpoint"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Swegon CASA Genius",
            model="CASA Genius",
        )

    @property
    def native_value(self) -> float | None:
        """Return current setpoint in celcius."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("temperature_setpoint")

    async def async_set_native_value(self, value: float) -> None:
        """Write new setpoint to the device."""
        _LOGGER.debug(
            "Setting temperature setpoint to %.1f °C (raw: %d)", value, int(value * 10)
        )
        await self.coordinator.async_write_temp_setpoint(value)
