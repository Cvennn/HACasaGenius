"""Async Modbus RTU client for Swegon GENIUS over RS-485 USB adapter."""

from __future__ import annotations

import logging

from pymodbus.client import AsyncModbusSerialClient
from pymodbus.exceptions import ModbusException

_LOGGER = logging.getLogger(__name__)

def _to_signed16(value):
    if value >= 0x8000:
        return value - 0x10000
    return value

class SwegonModbusClient:
    def __init__(self, port, slave, baudrate=38400, stopbits=1, parity="N", bytesize=8, timeout=5):
        self._port = port
        self._slave = slave
        self._client = AsyncModbusSerialClient(
            port=port,
            baudrate=baudrate,
            stopbits=stopbits,
            bytesize=bytesize,
            parity=parity,
            timeout=timeout,
        )

    async def connect(self) -> bool:
        connected = await self._client.connect()
        if connected:
            _LOGGER.debug("Modbus connected on %s (slave %s)", self._port, self._slave)
        else:
            _LOGGER.error("Modbus connection failed on %s", self._port)
        return connected

    async def disconnect(self) -> None:
        self._client.close()
        _LOGGER.debug("Modbus connection closed")

    @property
    def connected(self) -> bool:
        return self._client.connected

    async def read_input_register(self, address):
        try:
            r = await self._client.read_input_registers(address, count=1)
            if r.isError():
                return None
            return r.registers[0]
        except Exception as e:
            _LOGGER.error("read_input_register %d: %s", address, e)
            return None

    async def read_input_registers(self, address, count):
        try:
            r = await self._client.read_input_registers(address, count=count)
            if r.isError():
                return None
            return r.registers
        except Exception as e:
            _LOGGER.error("read_input_registers %d: %s", address, e)
            return None

    async def read_holding_register(self, address):
        try:
            r = await self._client.read_holding_registers(address, count=1)
            if r.isError():
                return None
            return r.registers[0]
        except Exception as e:
            _LOGGER.error("read_holding_register %d: %s", address, e)
            return None

    async def write_register(self, address, value):
        try:
            r = await self._client.write_register(address, value)
            if r.isError():
                return False
            return True
        except Exception as e:
            _LOGGER.error("write_register %d: %s", address, e)
            return False

    @staticmethod
    def apply_scale(raw, scale, signed=False):
        if signed:
            raw = _to_signed16(raw)
        return raw * scale

    @staticmethod
    def extract_bit(value, bit):
        return bool((value >> bit) & 1)

    @staticmethod
    def ascii_registers_to_string(registers):
        chars = []
        for reg in registers:
            high = (reg >> 8) & 0xFF
            low = reg & 0xFF
            if high:
                chars.append(chr(high))
            if low:
                chars.append(chr(low))
        return "".join(chars).strip()

    async def read_device_info(self):
        info = {}
        major = await self.read_input_register(6000)
        minor = await self.read_input_register(6001)
        build = await self.read_input_register(6002)
        if major is not None:
            info["firmware"] = f"{major}.{minor}.{build}"
        model_regs = await self.read_input_registers(6007, 15)
        info["model"] = (
            self.ascii_registers_to_string(model_regs)
            if model_regs
            else "Swegon CASA Genius"
        )
        serial_regs = await self.read_input_registers(6023, 24)
        info["serial_number"] = (
            self.ascii_registers_to_string(serial_regs) if serial_regs else None
        )
        return info


# Version check
try:
    import pymodbus
    import logging

    logging.getLogger("custom_components.swegon_genius").warning(
        "pymodbus versio: %s", pymodbus.__version__
    )
except Exception:
    pass
