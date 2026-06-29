"""Swegon CASA Genius - Diagnostics."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """
    Return diagnostics for a config entry.

    This includes the config entry settings (with only the port, slave and
    baudrate fields), the device info and the current coordinator data.
    """
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
