"""Swegon CASA Genius - Diagnostics."""
from __future__ import annotations
from typing import Any
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    return {
        "config_entry": {
            "port": entry.data.get("port"),
            "slave": entry.data.get("slave"),
            "baudrate": entry.data.get("baudrate"),
        },
        "device_info": coordinator.device_info_data,
        "data": coordinator.data,
    }
