"""Select platform for Swegon CASA Genius."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    BOOST_TIMER_OPTIONS,
    DOMAIN,
    EMERGENCY_STOP_OPTIONS,
    FIREPLACE_LEVELS,
    OPERATION_MODES_WRITE,
    RH_LEVELS,
    SUMMER_BOOST_LEVELS,
    VENTILATION_TO_MODE,
    VOC_AUTOMATION_LEVELS,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import SwegonCoordinator

SELECT_DEFS = [
    {
        "key": "operating_mode",
        "name": "Kayttotila",
        "address": 5000,
        "options": OPERATION_MODES_WRITE,
        "read_key": "ventilation_state",
        "read_map": VENTILATION_TO_MODE,
    },
    {
        "key": "rh_automation",
        "name": "RH-automaatio",
        "address": 5009,
        "options": RH_LEVELS,
        "read_key": "rh_automation",
    },
    {
        "key": "voc_automation",
        "name": "VOC-automaatio",
        "address": 5010,
        "options": VOC_AUTOMATION_LEVELS,
        "read_key": "voc_automation",
    },
    {
        "key": "summer_boost",
        "name": "Kesatilan tehostus",
        "address": 5168,
        "options": SUMMER_BOOST_LEVELS,
        "read_key": "summer_boost",
    },
    {
        "key": "boost_timer",
        "name": "Tehostusajastin",
        "address": 5101,
        "options": BOOST_TIMER_OPTIONS,
        "read_key": "boost_timer",
    },
    {
        "key": "emergency_stop",
        "name": "Hatapysaytys tila",
        "address": 5017,
        "options": EMERGENCY_STOP_OPTIONS,
        "read_key": "emergency_stop",
    },
    {
        "key": "fireplace_level",
        "name": "Takan teho",
        "address": 5104,
        "options": FIREPLACE_LEVELS,
        "read_key": "fireplace_level",
    },
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Swegon Genius select entities from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SwegonSelect(coordinator, entry, d) for d in SELECT_DEFS])


class SwegonSelect(CoordinatorEntity, SelectEntity):
    """Representation of a Swegon Genius select entity."""

    def __init__(
        self, coordinator: SwegonCoordinator, entry: ConfigEntry, sel_def: dict
    ) -> None:
        """Initialize the Swegon Genius select entity."""
        super().__init__(coordinator)
        self._def = sel_def
        self._options_map = sel_def["options"]  # {arvo: teksti}
        self._read_map = sel_def.get("read_map", sel_def["options"])
        self._reverse = {v: k for k, v in self._options_map.items()}  # {teksti: arvo}
        self._attr_unique_id = f"{entry.entry_id}_{sel_def['key']}"
        self._attr_name = sel_def["name"]
        self._attr_options = list(self._options_map.values())
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Swegon",
            model=coordinator.device_info_data.get("model", "CASA Genius"),
            sw_version=coordinator.device_info_data.get("firmware"),
        )

    @property
    def current_option(self) -> str | None:
        """
        Return current mode as raw using the read_map.

        For operation_mode: coordinator stores the raw int from 3x6434.
        read_map covers all states including Fireplace (read-only).
        Returns None if data unavailable.
        """
        raw = self.coordinator.data.get(self._def["read_key"])
        if raw is None:
            return None
        return self._read_map.get(raw)

    async def async_select_option(self, option: str) -> None:
        """
        Write the selected option to the device.

        Maps option string → integer via write_map, then calls the
        appropriate coordinator write method.
        """
        value = self._reverse.get(option)
        if value is None:
            return
        await self.coordinator.client.write_register(self._def["address"], value)  # pyright: ignore[reportAttributeAccessIssue]
        await self.coordinator.async_request_refresh()
