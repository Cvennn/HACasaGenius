"""DataUpdateCoordinator for Swegon GENIUS."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DEFAULT_SCAN_INTERVAL,
    HEATING_STATES,
    OPERATION_MODES_READ,
    UNIT_STATES,
)
from .registers_genius import (
    ALARM_REGISTERS,
    CONTROL_REGISTERS,
    ENUM_SENSORS,
    SENSOR_REGISTERS,
    STATUS_REGISTERS,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from .modbus_client import SwegonModbusClient


ENUM_MAPS = {
    "UNIT_STATES": UNIT_STATES,
    "HEATING_STATES": HEATING_STATES,
    "VENTILATION_STATES": OPERATION_MODES_READ,
}
_LOGGER = logging.getLogger(__name__)


class SwegonCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, client: SwegonModbusClient, device_info: dict[str, Any]) -> None:
        super().__init__(
            hass, _LOGGER,
            name="Swegon CASA Genius",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.client = client
        self.device_info_data = device_info

    async def _async_update_data(self) -> dict[str, Any]:
        # Fetch and scale all registers. Raises UpdateFailed on any error
        if not self.client.connected:
            connected = await self.client.connect()
            if not connected:
                raise UpdateFailed("Cannot connect to Swegon GENIUS via Modbus")

        data: dict[str, Any] = {}

        try:
            for sensor in SENSOR_REGISTERS:
                if sensor["type"] == "input":
                    raw = await self.client.read_input_register(sensor["address"])
                else:
                    raw = await self.client.read_holding_register(sensor["address"])
                if raw is not None:
                    signed = sensor.get("data_type") == "int16"
                    data[sensor["key"]] = self.client.apply_scale(raw, sensor["scale"], signed=signed)
                else:
                    data[sensor["key"]] = None

            # Tilarekisterit (raaka)
            for key, reg in STATUS_REGISTERS.items():
                data[key] = await self.client.read_input_register(reg["address"])

            # Enum-tekstisensorit -> key+"_text"
            for es in ENUM_SENSORS:
                raw = await self.client.read_input_register(es["address"])
                mapping = ENUM_MAPS.get(es["map"], {})
                data[es["key"] + "_text"] = mapping.get(raw) if raw is not None else None

            # Ohjausrekisterit
            for key, reg in CONTROL_REGISTERS.items():
                address = reg.get("address") or reg.get("read_address") or reg.get("write_address")
                if address is None:
                    continue
                if reg.get("type", "holding") == "holding":
                    raw = await self.client.read_holding_register(address)
                else:
                    raw = await self.client.read_input_register(address)
                scale = reg.get("scale")
                if raw is not None and scale and scale != 1.0:
                    data[key] = self.client.apply_scale(raw, scale)
                else:
                    data[key] = raw

            # Bittimaskihalytykset
            for alarm_reg in ALARM_REGISTERS:
                raw = await self.client.read_input_register(alarm_reg["register"])
                for bit, info in alarm_reg["bits"].items():
                    data[info["key"]] = self.client.extract_bit(raw, bit) if raw is not None else None

        except Exception as e:
            raise UpdateFailed(f"Virhe Modbus-datan haussa: {e}") from e

        return data