"""Swegon GENIUS Home Assistant integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import CONF_BAUDRATE, CONF_PARITY, CONF_SLAVE, CONF_STOPBITS, DOMAIN
from .coordinator import SwegonCoordinator
from .modbus_client import SwegonModbusClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    # Platform.SENSOR,
    # Platform.BINARY_SENSOR,
    # Platform.SELECT,
    # Platform.NUMBER,
    # Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Swegon GENIUS from a config entry."""
    if CONF_PORT not in entry.data or CONF_SLAVE not in entry.data:
        _LOGGER.error(
            "Config entry %s is missing required data and will be removed",
            entry.entry_id,
        )
        await hass.config_entries.async_remove(entry.entry_id)
        return False

    client = SwegonModbusClient(
        port=entry.data[CONF_PORT],
        slave=entry.data[CONF_SLAVE],
        baudrate=entry.data[CONF_BAUDRATE],
        stopbits=entry.data[CONF_STOPBITS],
        parity=entry.data[CONF_PARITY],
    )

    connected = await client.connect()
    if not connected:
        raise ConfigEntryNotReady(
            f"Ei saada yhteyttä Swegon CASA Genius -laitteeseen portissa {entry.data[CONF_PORT]}"
        )

    device_info = await client.read_device_info()
    _LOGGER.info(
        "Yhdistetty Swegon CASA Genius: %s, firmware %s, sarjanumero %s",
        device_info.get("model"),
        device_info.get("firmware"),
        device_info.get("serial_number"),
    )

    coordinator = SwegonCoordinator(hass, client, device_info)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Swegon GENIUS config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        coordinator: SwegonCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.client.disconnect()

    return unload_ok
