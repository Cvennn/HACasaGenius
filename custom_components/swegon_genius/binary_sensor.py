"""Binary sensor platform for swegon_genius."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SwegonGeniusCoordinator
from .registers_genius import ALARM_REGISTERS, STATUS_BINARY_REGISTERS

_LOGGER = logging.getLogger(__name__)
RESERVED_CODE = ["RSVD"]


@dataclass(frozen=True, kw_only=True)
class SwegonBinarySensorDescription(BinarySensorEntityDescription):
    """Swegon GENIUS binary sensor entity."""

    coordinator_key: str = ""
    bit_postion: int | None = None
    is_flag: bool = False


def build_descriptions() -> list[SwegonBinarySensorDescription]:
    """Build binary sensor descriptions for the Swegon GENIUS integration."""
    descriptions: list[SwegonBinarySensorDescription] = []

    for word_key, reg in ALARM_REGISTERS.items():
        for bit_pos, (alarm_code, alarm_name) in reg["bits"].items():
            if alarm_code in RESERVED_CODE:
                continue
            descriptions.append(
                SwegonBinarySensorDescription(
                    key=f"{word_key}_bit{bit_pos}",
                    coordinator_key=word_key,
                    bit_postion=bit_pos,
                    name=f"{alarm_name} {alarm_code}",
                    device_class=BinarySensorDeviceClass.PROBLEM,
                    is_flag=False,
                )
            )

    for flag_key, reg in STATUS_BINARY_REGISTERS.items():
        descriptions.append(
            SwegonBinarySensorDescription(
                key=flag_key,
                coordinator_key=flag_key,
                bit_postion=None,
                name=reg["name"],
                device_class=BinarySensorDeviceClass.PROBLEM,
                is_flag=True,
            )
        )

    return descriptions


BINARY_SENSOR_DESCRIPTIONS = build_descriptions()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensor entities from a config entry."""
    coordinator: SwegonGeniusCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        SwegonGeniusBinarySensor(coordinator, entry, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class SwegonGeniusBinarySensor(
    CoordinatorEntity[SwegonGeniusCoordinator], BinarySensorEntity
):
    """Representation of a Swegon GENIUS binary sensor."""

    entity_description: SwegonBinarySensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SwegonGeniusCoordinator,
        entry: ConfigEntry,
        description: SwegonBinarySensorDescription,
    ) -> None:
        """
        Initialize the Swegon GENIUS binary sensor entity.

        Args :
            coordinator: The integration data coordinator.
            entry: The config entry for this integration instance.
            description: The binary sensor entity description.
        """
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
        """Return True if the binary sensor is on, False if off, or None if state is unknown."""
        if self.coordinator.data is None:
            return None

        desc = self.entity_description
        if desc.is_flag:
            value = self.coordinator.data.get(desc.coordinator_key)
            return bool(value) if value is not None else None

        alarm_dict: dict[str, bool] | None = self.coordinator.data.get(
            desc.coordinator_key
        )
        if alarm_dict is None:
            return None

        alarm_name_key: str = desc.name if isinstance(desc.name, str) else ""
        parts = alarm_name_key.split(" ", 1)
        description_part = parts[1] if len(parts) > 1 else alarm_name_key
        return alarm_dict.get(description_part)
