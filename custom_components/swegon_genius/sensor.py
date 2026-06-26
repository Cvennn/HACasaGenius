from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .registers_genius import ENUM_SENSORS, SENSOR_REGISTERS


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
    def __init__(self, coordinator, entry, sensor_def):
        super().__init__(coordinator)
        self._def = sensor_def
        self._attr_unique_id = f"{entry.entry_id}_{sensor_def['key']}"
        self._attr_name = sensor_def["name"]
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
    def native_value(self):
        return self.coordinator.data.get(self._def["key"])


class SwegonEnumSensor(CoordinatorEntity, SensorEntity):
    """Tekstimuotoinen tilasensori (esim. Yksikon tila, Lammitystila)."""

    def __init__(self, coordinator, entry, sensor_def):
        super().__init__(coordinator)
        self._def = sensor_def
        self._attr_unique_id = f"{entry.entry_id}_{sensor_def['key']}_text"
        self._attr_name = sensor_def["name"]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Swegon",
            model=coordinator.device_info_data.get("model", "CASA Genius"),
            sw_version=coordinator.device_info_data.get("firmware"),
        )

    @property
    def native_value(self):
        return self.coordinator.data.get(self._def["key"] + "_text")
