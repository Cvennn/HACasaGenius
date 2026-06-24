"""Config flow for Swegon GENIUS."""

from __future__ import annotations

import voluptuous as vol
import logging
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.core import callback

from .const import (
    CONF_BAUDRATE,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_SLAVE,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .modbus_client import SwegonGeniusModbusClient

_LOGGER = logging.getLogger(__name__)


class SwegonGeniusConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            client = SwegonGeniusModbusClient(
                port=user_input[CONF_PORT],
                slave=user_input[CONF_SLAVE],
                baudrate=user_input[CONF_BAUDRATE],
            )

            try:
                connected = await client.connect()

                if not connected:
                    errors["base"] = "cannot_connect"
                else:
                    # Read a register that should always exist
                    firmware_major = await client.read_single_input(6001)
                    firmware_minor = await client.read_single_input(6002)
                    firmware_build = await client.read_single_input(6003)
                    _LOGGER.debug("Firmware major: %s", firmware_major)
                    _LOGGER.debug("Firmware minor: %s", firmware_minor)
                    _LOGGER.debug("Firmware build: %s", firmware_build)
                    if firmware_major is None:
                        errors["base"] = "invalid_device"
                    else:
                        await self.async_set_unique_id(
                            f"{user_input[CONF_PORT]}_{user_input[CONF_SLAVE]}"
                        )
                        self._abort_if_unique_id_configured()

                        return self.async_create_entry(
                            title=f"Casa Genius ({user_input[CONF_PORT]})",
                            data=user_input,
                        )

            except Exception:
                errors["base"] = "unknown"

            finally:
                await client.close()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): str,
                    vol.Required(CONF_SLAVE, default=1): vol.All(
                        vol.Coerce(int),
                    ),
                    vol.Required(CONF_BAUDRATE, default=38400): vol.All(
                        vol.Coerce(int)
                    ),
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=DEFAULT_SCAN_INTERVAL,
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=5, max=300),
                    ),
                }
            ),
            errors=errors,
        )
