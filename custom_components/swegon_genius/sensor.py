"""
Sensor platform for Swegon CASA Genius integration.

21 measurement sensors sourced from SENSOR_REGISTERS + UNIT_STATUS_REGISTERS.
All values are pre-scaled by coordinator.py — sensor.py reads them as-is.

Bronze requirements:
  - unique_id for every entity
  - native_unit_of_measurement
  - device_class if applicable
  - state_class = measurement (for history graphs)
  - CoordinatorEntity base (automatic unavailable on poll failure)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    REVOLUTIONS_PER_MINUTE,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfVolumeFlowRate,
    )
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SwegonGeniusCoordinator
from .registers_genius import SENSOR_REGISTERS, UNIT_STATUS_REGISTERS

_LOGGER = logging.getLogger(__name__)
# Entity description dataclass — extends SensorEntityDescription with the
# coordinator data key so we can look up the right value from coordinator.data

@dataclass(frozen=True, kw_only=True)
class SwegonSensorEntityDescription(SensorEntityDescription):
    """Entity description."""

    coordinator_key: str = ""
    value_map: dict[int, str] | None = None


# Build entity descriptions from registers_genius.py
# Map unit strings from registers_genius.py
_UNIT_MAP: dict[str | None, str | None] = {
    "°C": UnitOfTemperature.CELSIUS,
    "%": PERCENTAGE,
    "ppm": CONCENTRATION_PARTS_PER_MILLION,
    "Pa": UnitOfPressure.PA,
    "l/s": UnitOfVolumeFlowRate.LITERS_PER_SECOND,
    "rpm": REVOLUTIONS_PER_MINUTE,
    "min": "min",
    "d": "d",
    "h": "h",
    "W": "W",
    "m³/h": "m³/h",
    None: None,
}

# Map device_class strings from registers_genius.py to HA SensorDeviceClass
_DEVICE_CLASS_MAP: dict[str | None, SensorDeviceClass | None] = {
    "temperature": SensorDeviceClass.TEMPERATURE,
    "humidity": SensorDeviceClass.HUMIDITY,
    "carbon_dioxide": SensorDeviceClass.CO2,
    "pressure": SensorDeviceClass.PRESSURE,
    "power": SensorDeviceClass.POWER,
    None: None,
}


def _build_descriptions() -> list[SwegonSensorEntityDescription]:
    """Generate SensorEntityDescription list from register dicts."""
    descriptions: list[SwegonSensorEntityDescription] = []

    # sensors from SENSOR_REGISTERS
    for key, reg in SENSOR_REGISTERS.items():
        unit_str = reg.get("unit")
        dc_str = reg.get("device_class")

        descriptions.append(
            SwegonSensorEntityDescription(
                key=key,
                coordinator_key=key,
                name=reg["name"],
                native_unit_of_measurement=_UNIT_MAP.get(unit_str, unit_str),
                device_class=_DEVICE_CLASS_MAP.get(dc_str),
                state_class=SensorStateClass.MEASUREMENT,
                suggested_display_precision=1 if reg.get("scale", 1) != 1 else 0,
            )
        )

    # unit_state from UNIT_STATUS_REGISTERS
    descriptions.append(
        SwegonSensorEntityDescription(
            key="unit_state",
            coordinator_key="unit_state",
            name="Unit State",
            native_unit_of_measurement=None,
            device_class=SensorDeviceClass.ENUM,
            state_class=None,
            options=[
                "Critical Stop",
                "User Stopped",
                "Starting",
                "Normal",
                "Commissioning",
            ],
            value_map=UNIT_STATUS_REGISTERS["unit_state"]["states"],
        )
    )

    descriptions.append(
        SwegonSensorEntityDescription(
            key="boost_time_left",
            coordinator_key="boost_time_left",
            name="Boost Time Left",
            native_unit_of_measurement="min",
            device_class=None,
            state_class=SensorStateClass.MEASUREMENT,
        )
    )

    return descriptions


SENSOR_DESCRIPTIONS: list[SwegonSensorEntityDescription] = _build_descriptions()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Swegon GENIUS sensor entities from a config entry."""
    coordinator: SwegonGeniusCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        SwegonGeniusSensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class SwegonGeniusSensor(CoordinatorEntity[SwegonGeniusCoordinator], SensorEntity):
    entity_description: SwegonSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SwegonGeniusCoordinator,
        entry: ConfigEntry,
        description: SwegonSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description

        # Format: <domain>_<config_entry_id>_<register_key>
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_{description.key}"

        # Device info — groups all entities under one device in HA device registry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Swegon CASA Genius",
            manufacturer="Swegon",
            model="CASA Genius",
            sw_version=coordinator.data.get("firmware_version")
            if coordinator.data
            else None,
        )

    @property
    def native_value(self) -> float | int | str | None:
        if self.coordinator.data is None:
            return None

        value = self.coordinator.data.get(self.entity_description.coordinator_key)

        if value is None:
            return None

        # Map raw int to string for enum sensors
        if self.entity_description.value_map is not None:
            return self.entity_description.value_map.get(value, f"Unknown ({value})")

        return value

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        reg = SENSOR_REGISTERS.get(self.entity_description.coordinator_key)
        if reg:
            return {
                "modbus_address": reg["address"],
                "modbus_type": reg["type"],
            }
        return None
