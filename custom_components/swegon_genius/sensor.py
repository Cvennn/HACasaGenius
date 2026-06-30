"""Sensor platform for Swegon CASA Genius."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .registers_genius import ENUM_SENSORS, SENSOR_REGISTERS

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Swegon Genius sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [SwegonSensor(coordinator, entry, s) for s in SENSOR_REGISTERS]
    entities += [SwegonEnumSensor(coordinator, entry, s) for s in ENUM_SENSORS]
    async_add_entities(entities)


class SwegonSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Swegon Genius sensor."""

    def __init__(
        self,
        coordinator: Any,
        entry: ConfigEntry,
        sensor_def: dict[str, Any],
    ) -> None:
        """Initialize a Swegon Genius sensor."""
        super().__init__(coordinator)

        self._def = sensor_def

        self._attr_unique_id = f"{entry.entry_id}_{sensor_def['key']}"
        self._attr_has_entity_name = True
        self._attr_translation_key = sensor_def["translation_key"]

        self._attr_native_unit_of_measurement = sensor_def.get("unit")

        if sensor_def.get("device_class"):
            self._attr_device_class = sensor_def["device_class"]

        if sensor_def.get("state_class"):
            self._attr_state_class = sensor_def["state_class"]

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Swegon",
            model=coordinator.device_info_data.get("model", "CASA Genius"),
            sw_version=coordinator.device_info_data.get("firmware"),
        )

    @property
    def native_value(self) -> Any:
        """Return the native value of the sensor."""
        return self.coordinator.data.get(self._def["key"])


class SwegonEnumSensor(CoordinatorEntity, SensorEntity):
    """Text based state sensors."""

    def __init__(
        self,
        coordinator: Any,
        entry: ConfigEntry,
        sensor_def: dict[str, Any],
    ) -> None:
        """Initialize a Swegon Genius enum sensor."""
        super().__init__(coordinator)
        self._def = sensor_def
        self._attr_unique_id = f"{entry.entry_id}_{sensor_def['key']}_text"
        self._attr_has_entity_name = True
        self._attr_translation_key = sensor_def["translation_key"]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Swegon",
            model=coordinator.device_info_data.get("model", "CASA Genius"),
            sw_version=coordinator.device_info_data.get("firmware"),
        )

    @property
    def native_value(self) -> Any:
        """Return the native text value of the sensor."""
        return self.coordinator.data.get(self._def["key"] + "_text")
