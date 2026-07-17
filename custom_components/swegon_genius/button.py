"""Button platform for Swegon Genius."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .registers_genius import ALARM_CONFIRM_REGISTERS

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Swegon Genius alarm-confirm button entities from a config entry."""
    coordinator = entry.runtime_data
    async_add_entities(
        SwegonAlarmConfirmButton(coordinator, entry, key, reg)
        for key, reg in ALARM_CONFIRM_REGISTERS.items()
    )


class SwegonAlarmConfirmButton(CoordinatorEntity, ButtonEntity):
    """Button that confirms/acknowledges a single Swegon Genius alarm."""

    def __init__(
        self,
        coordinator: Any,
        entry: ConfigEntry,
        key: str,
        reg_def: dict,
    ) -> None:
        """Initialize the alarm-confirm button."""
        super().__init__(coordinator)
        self._key = key
        self._address = reg_def["address"]
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_has_entity_name = True
        self._attr_translation_key = key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Swegon",
            model=coordinator.device_info_data.get("model", "CASA Genius"),
            sw_version=coordinator.device_info_data.get("firmware"),
        )

    async def async_press(self) -> None:
        """Write 1 to the alarm-confirm register to acknowledge the alarm."""
        await self.coordinator.client.write_register(self._address, 1)
        await self.coordinator.async_request_refresh()
