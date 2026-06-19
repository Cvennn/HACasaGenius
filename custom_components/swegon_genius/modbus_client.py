"""Async Modbus RTU client for Swegon GENIUS over RS-485 USB adapter."""

from __future__ import annotations

import logging
from typing import Any

from pymodbus.client import AsyncModbusSerialClient
from pymodbus.exceptions import ModbusException

_LOGGER = logging.getLogger(__name__)


class SwegonGeniusModbusClient:
    def __init__(
        self,
        port: str,
        slave: int,
        baudrate: int = 38400,
    ) -> None:
        self._port = port
        self._slave = slave
        self._client = AsyncModbusSerialClient(
            port=port,
            baudrate=baudrate,
            bytesize=8,
            parity="N",
            stopbits=1,
        )

    async def connect(self) -> bool:
        connected = await self._client.connect()
        if connected:
            _LOGGER.debug("Modbus connected on %s (slave %s)", self._port, self._slave)
        else:
            _LOGGER.error("Modbus connection failed on %s", self._port)
        return connected

    async def close(self) -> None:
        self._client.close()
        _LOGGER.debug("Modbus connection closed")

    @property
    def connected(self) -> bool:
        return self._client.connected

    async def read_input_registers(
        self, address: int, count: int = 1
    ) -> list[int] | None:
        """Read input registers (3x). Returns list of raw integer values or None on error."""
        _LOGGER.debug(
            "Reading input register %s using device_id=%s",
            address,
            self._slave,
        )
        try:
            result = await self._client.read_input_registers(
                address=address, count=count, device_id=self._slave
            )
            if result.isError():
                _LOGGER.warning(
                    "Error reading input register %s (count=%s): %s",
                    address,
                    count,
                    result,
                )
                return None
            return result.registers
        except ModbusException as err:
            _LOGGER.error(
                "Modbus exception reading input register %s: %s", address, err
            )
            return None

    async def read_holding_registers(
        self, address: int, count: int = 1
    ) -> list[int] | None:
        try:
            result = await self._client.read_holding_registers(
                address=address, count=count, device_id=self._slave
            )
            if result.isError():
                _LOGGER.warning(
                    "Error reading holding register %s (count=%s): %s",
                    address,
                    count,
                    result,
                )
                return None
            return result.registers
        except ModbusException as err:
            _LOGGER.error(
                "Modbus exception reading holding register %s: %s", address, err
            )
            return None

    async def write_holding_register(self, address: int, value: int) -> bool:
        try:
            result = await self._client.write_register(
                address=address, value=value, device_id=self._slave
            )
            if result.isError():
                _LOGGER.warning(
                    "Error writing holding register %s = %s: %s", address, value, result
                )
                return False
            _LOGGER.debug("Wrote register %s = %s", address, value)
            return True
        except ModbusException as err:
            _LOGGER.error(
                "Modbus exception writing holding register %s = %s: %s",
                address,
                value,
                err,
            )
            return False

    async def read_single_input(self, address: int) -> int | None:
        regs = await self.read_input_registers(address, count=1)
        return regs[0] if regs is not None else None

    async def read_single_holding(self, address: int) -> int | None:
        regs = await self.read_holding_registers(address, count=1)
        return regs[0] if regs is not None else None
