"""Binary sensor platform for swegon_genius."""  # noqa: EXE002

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .registers_genius import ALARM_REGISTERS

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the swegon_genius binary sensor entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for alarm_reg in ALARM_REGISTERS:
        entities.extend(
            SwegonBinarySensor(coordinator, entry, info["key"], info["name"])
            for info in alarm_reg["bits"].values()
        )
    async_add_entities(entities)


class SwegonBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Swegon Genius alarm binary sensor."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(
        self, coordinator: Any, entry: ConfigEntry, key: str, name: str
    ) -> None:
        """Initialize the Swegon Genius binary sensor."""
        super().__init__(coordinator)
        self._key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_name = name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Swegon",
            model=coordinator.device_info_data.get("model", "CASA Genius"),
            sw_version=coordinator.device_info_data.get("firmware"),
        )

    @property
    def is_on(self) -> bool | None:
        """Return True if the binary sensor is on."""
        return self.coordinator.data.get(self._key)
