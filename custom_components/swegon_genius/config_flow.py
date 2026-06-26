"""Config flow for Swegon GENIUS."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_BAUDRATE,
    CONF_PARITY,
    CONF_SLAVE,
    CONF_STOPBITS,
    DEFAULT_BAUDRATE,
    DEFAULT_PARITY,
    DEFAULT_PORT,
    DEFAULT_SLAVE,
    DEFAULT_STOPBITS,
    DOMAIN,
)
from .modbus_client import SwegonModbusClient

_LOGGER = logging.getLogger(__name__)


STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PORT, default=DEFAULT_PORT): str,
        vol.Required(CONF_SLAVE, default=DEFAULT_SLAVE): vol.All(vol.Coerce(int)),
        vol.Required(CONF_BAUDRATE, default=DEFAULT_BAUDRATE): vol.In([9600, 19200, 38400, 57600, 115200]),
        vol.Required(CONF_STOPBITS, default=DEFAULT_STOPBITS): vol.In([1, 2]),
        vol.Required(CONF_PARITY, default=DEFAULT_PARITY): vol.In(["N", "E", "O"]),
    }
)


async def _test_connection(hass: HomeAssistant, data: dict[str, Any]) -> str | None:
    client = SwegonModbusClient(
        port=data[CONF_PORT],
        slave=data[CONF_SLAVE],
        baudrate=data[CONF_BAUDRATE],
        stopbits=data[CONF_STOPBITS],
        parity=data[CONF_PARITY],
    )
    try:
        connected = await client.connect()
        if not connected:
            return "cannot_connect"
        # Yhteys avautui — riittää
        return None
    except Exception as e:
        _LOGGER.error("Yhteystesti epäonnistui: %s", e)
        return "cannot_connect"
    finally:
        await client.disconnect()


class SwegonConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_PORT]}_{user_input[CONF_SLAVE]}")
            self._abort_if_unique_id_configured()
            error = await _test_connection(self.hass, user_input)
            if error:
                errors["base"] = error
            else:
                return self.async_create_entry(
                    title=f"Swegon CASA Genius ({user_input[CONF_PORT]})",
                    data=user_input) # type: ignore
        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_SCHEMA, errors=errors) # type: ignore
