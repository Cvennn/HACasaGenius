"""Select platform for Swegon CASA Genius."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SwegonGeniusCoordinator
from .registers_genius import SELECT_REGISTERS

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class SwegonSelectDescription(SelectEntityDescription):
    """Select entity description."""

    coordinator_key: str = ""
    write_map: dict[str, int] = field(default_factory=dict)
    read_map: dict[int, str] = field(default_factory=dict)


def invert(d: dict[int, str]) -> dict[str, int]:
    return {v: k for k, v in d.items()}


SELECT_DESCRIPTIONS: list[SwegonSelectDescription] = [
    SwegonSelectDescription(
        key="operation_mode",
        coordinator_key="operation_mode",
        name="Operation Mode",
        icon="mdi:air-filter",
        options=list(SELECT_REGISTERS["operation_mode"]["write_options"].values()),
        write_map=invert(SELECT_REGISTERS["operation_mode"]["write_options"]),
        read_map=SELECT_REGISTERS["operation_mode"]["read_states"],
    ),
    SwegonSelectDescription(
        key="rh_automation",
        coordinator_key="rh_automation",
        name="RH Automation level",
        icon="mdi:water-percent",
        options=list(SELECT_REGISTERS["rh_automation"]["write_options"].values()),
        write_map=invert(SELECT_REGISTERS["rh_automation"]["write_options"]),
        read_map=SELECT_REGISTERS["rh_automation"]["read_states"],
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up select entities from a config entry."""
    coordinator: SwegonGeniusCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        SwegonGeniusSelect(coordinator, entry, description)
        for description in SELECT_DESCRIPTIONS
    )


class SwegonGeniusSelect(CoordinatorEntity[SwegonGeniusCoordinator], SelectEntity):
    """Select entity for operation mode or RH automation."""

    entity_description: SwegonSelectDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SwegonGeniusCoordinator,
        entry: ConfigEntry,
        description: SwegonSelectDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_{description.key}"
        self._attr_options = list(description.options or [])
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Swegon CASA Genius",
            model="CASA Genius",
        )

    @property
    def current_option(self) -> str | None:
        """
        Return current mode as a string using the read_map.

        For operation_mode: coordinator stores the raw int from 3x6434.
        read_map covers all states including Fireplace (read-only).
        Returns None if data unavailable.
        """
        if self.coordinator.data is None:
            return None

        raw = self.coordinator.data.get(self.entity_description.coordinator_key)
        _LOGGER.debug("Current option raw: %s", raw)
        if raw is None:
            return None

        option = self.entity_description.read_map.get(raw)
        if option is None:
            _LOGGER.warning(
                "%s: unknown raw value %s from device", self.entity_description.key, raw
            )
            return f"Unknown ({raw})"
        return option

    async def async_select_option(self, option: str) -> None:
        """
        Write the selected option to the device.

        Maps option string → integer via write_map, then calls the
        appropriate coordinator write method.
        """
        write_value = self.entity_description.write_map.get(option)
        if write_value is None:
            _LOGGER.error(
                "%s: cannot write option '%s' — not in write_map",
                self.entity_description.key,
                option,
            )
            return

        _LOGGER.debug(
            "Select %s: '%s' → raw %d", self.entity_description.key, option, write_value
        )

        if self.entity_description.key == "operation_mode":
            await self.coordinator.async_write_operation_mode(write_value)
        elif self.entity_description.key == "rh_automation":
            await self.coordinator.async_write_rh_level(write_value)
        else:
            _LOGGER.error(
                "No write handler for select key: %s", self.entity_description.key
            )
