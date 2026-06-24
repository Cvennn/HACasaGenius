"""DataUpdateCoordinator for Swegon GENIUS."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any, TYPE_CHECKING

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .registers_genius import (
    ALARM_REGISTERS,
    NUMBER_REGISTERS,
    SELECT_REGISTERS,
    SENSOR_REGISTERS,
    SWITCH_REGISTERS,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from .modbus_client import SwegonGeniusModbusClient

_LOGGER = logging.getLogger(__name__)


class SwegonGeniusCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    # Coordinator that polls all Swegon GENIUS registers and scales them
    def __init__(
        self,
        hass: HomeAssistant,
        client: SwegonGeniusModbusClient,
        scan_interval: int,
    ) -> None:
        self.client = client
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        # Fetch and scale all registers. Raises UpdateFailed on any error
        if not self.client.connected:
            connected = await self.client.connect()
            if not connected:
                raise UpdateFailed("Cannot connect to Swegon GENIUS via Modbus")

        data: dict[str, Any] = {}

        try:
            await self._read_sensor_registers(data)
            await self._read_alarm_registers(data)
            await self._read_select_registers(data)
            await self._read_number_registers(data)
            await self._read_switch_registers(data)
        except Exception as err:
            raise UpdateFailed(f"Modbus poll failed: {err}") from err

        return data

    async def _read_sensor_registers(self, data: dict[str, Any]) -> None:
        for key, reg in SENSOR_REGISTERS.items():
            address = self.modbus_addr(reg["address"])
            raw = await self.client.read_single_input(address)
            if raw is None:
                _LOGGER.warning(
                    "No data for sensor register %s (%s)", key, reg["address"]
                )
                data[key] = None
                continue

            scale = reg.get("scale", 1)
            # Signed 16-bit handling (temperatures can be negative)
            if raw > 32767:
                raw -= 65536
            data[key] = round(raw * scale, 1) if scale != 1 else raw

        _LOGGER.debug("Sensor data: %s", {k: data[k] for k in SENSOR_REGISTERS})

    async def _read_alarm_registers(self, data: dict[str, Any]) -> None:
        for key, reg in ALARM_REGISTERS.items():
            address = self.modbus_addr(reg["address"])
            raw = await self.client.read_single_input(address)
            if raw is None:
                data[key] = {}
                continue

            # Expand bitmask into dict of {alarm_name: bool}
            bits: dict[str, bool] = {}
            for bit_pos, alarm_name in reg["bits"].items():
                bits[alarm_name] = bool(raw & (1 << bit_pos))
            data[key] = bits

        _LOGGER.debug("Alarm data: %s", {k: data[k] for k in ALARM_REGISTERS})

    async def _read_select_registers(self, data: dict[str, Any]) -> None:
        for key, reg in SELECT_REGISTERS.items():
            read_type = reg["read_type"]
            address = self.modbus_addr(reg["read_address"])

            if read_type == "input":
                raw = await self.client.read_single_input(address)
            else:
                raw = await self.client.read_single_holding(address)

            data[key] = raw  # raw int — entity maps via OPERATION_MODES / RH_LEVELS

        _LOGGER.debug("Select data: %s", {k: data[k] for k in SELECT_REGISTERS})

    async def _read_number_registers(self, data: dict[str, Any]) -> None:
        for key, reg in NUMBER_REGISTERS.items():
            address = self.modbus_addr(reg["address"])
            raw = await self.client.read_single_holding(address)
            if raw is None:
                data[key] = None
                continue
            scale = reg.get("scale", 1)
            data[key] = round(raw * scale, 1)

        _LOGGER.debug("Number data: %s", {k: data[k] for k in NUMBER_REGISTERS})

    async def _read_switch_registers(self, data: dict[str, Any]) -> None:
        for key, reg in SWITCH_REGISTERS.items():
            address = self.modbus_addr(reg["address"])
            raw = await self.client.read_single_holding(address)
            data[key] = bool(raw) if raw is not None else None

        _LOGGER.debug("Switch data: %s", {k: data[k] for k in SWITCH_REGISTERS})

    async def async_write_operation_mode(self, mode_int: int) -> None:
        """Write operation mode to 4x5001."""
        reg = SELECT_REGISTERS["operation_mode"]
        address = self.modbus_addr(reg["write_address"])
        ok = await self.client.write_holding_register(address, mode_int)
        if ok:
            await self.async_request_refresh()

    async def async_write_rh_level(self, level_int: int) -> None:
        """Write RH automation level to 4x5010."""
        reg = SELECT_REGISTERS["rh_automation"]
        address = self.modbus_addr(reg["write_address"])
        ok = await self.client.write_holding_register(address, level_int)
        if ok:
            await self.async_request_refresh()

    async def async_write_temp_setpoint(self, temp_celsius: float) -> None:
        """Write room temp setpoint to 4x5101. Raw value = temp × 10."""
        reg = NUMBER_REGISTERS["temperature_setpoint"]
        raw = round(temp_celsius * reg["write_scale"])
        address = self.modbus_addr(reg["address"])
        ok = await self.client.write_holding_register(address, raw)
        if ok:
            await self.async_request_refresh()

    async def async_write_switch(self, key: str, state: bool) -> None:
        """Write a switch register (CO2 automation or emergency stop)."""
        reg = SWITCH_REGISTERS[key]
        address = self.modbus_addr(reg["address"])
        ok = await self.client.write_holding_register(address, int(state))
        if ok:
            await self.async_request_refresh()

    def modbus_addr(self, register: int) -> int:
        """Convert address to modbus 0-based address."""
        return register - 1
