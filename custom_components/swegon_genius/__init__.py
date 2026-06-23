"""Swegon GENIUS Home Assistant integration."""

from __future__ import annotations  # noqa: I001

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    CONF_BAUDRATE,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_SLAVE,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    DEFAULT_BAUDRATE,
)
from .coordinator import SwegonGeniusCoordinator
from .modbus_client import SwegonGeniusModbusClient

LOGGER = logging.getLogger(__name__)
_LOGGER = LOGGER

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SELECT,
    # Platform.NUMBER,
    # Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Swegon GENIUS from a config entry."""
    # if CONF_PORT not in entry.data or CONF_SLAVE not in entry.data:
    #     LOGGER.error(
    #         "Config entry %s is missing required data and will be removed",
    #         entry.entry_id,
    #     )
    #     await hass.config_entries.async_remove(entry.entry_id)
    #     return False

    client = SwegonGeniusModbusClient(
        port=entry.data[CONF_PORT],
        slave=entry.data[CONF_SLAVE],
        baudrate=entry.data.get(CONF_BAUDRATE, DEFAULT_BAUDRATE),
    )

    connected = await client.connect()

    coordinator = SwegonGeniusCoordinator(
        hass=hass,
        client=client,
        scan_interval=entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    if connected:
        try:
            await coordinator.async_config_entry_first_refresh()
        except ConfigEntryNotReady:
            _LOGGER.warning(
                "Connection to Swegon GENIUS on %s failed during initial refresh",
                entry.data[CONF_PORT],
            )
    else:
        _LOGGER.warning(
            "Swegon GENIUS not reachable on %s; entities will remain unavailable until the device is present",
            entry.data[CONF_PORT],
        )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Swegon GENIUS config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        coordinator: SwegonGeniusCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.client.close()

    return unload_ok
