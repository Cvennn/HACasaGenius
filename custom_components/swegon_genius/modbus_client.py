"""Async Modbus RTU client for Swegon GENIUS over RS-485 USB adapter."""  # noqa: EXE002

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from pymodbus.client import AsyncModbusSerialClient

if TYPE_CHECKING:
    from collections.abc import Sequence

_LOGGER = logging.getLogger(__name__)


def _to_signed16(value: int) -> int:
    """Convert an unsigned 16-bit value to a signed 16-bit integer."""
    if value >= 0x8000:  # noqa: PLR2004
        return value - 0x10000
    return value


class SwegonModbusClient:
    """Async Modbus RTU client for the Swegon GENIUS device."""

    def __init__(self, port: str, slave: int, **kwargs: Any) -> None:
        """Initialize the Modbus client with serial connection settings."""
        self._port = port
        self._slave = slave
        baudrate = int(kwargs.pop("baudrate", 38400))
        stopbits = int(kwargs.pop("stopbits", 1))
        parity = str(kwargs.pop("parity", "N"))
        bytesize = int(kwargs.pop("bytesize", 8))
        timeout = float(kwargs.pop("timeout", 5))
        if kwargs:
            unexpected = ", ".join(sorted(kwargs))
            msg = f"Unexpected keyword arguments: {unexpected}"
            raise TypeError(msg)

        self._client = AsyncModbusSerialClient(
            port=port,
            baudrate=baudrate,
            stopbits=stopbits,
            bytesize=bytesize,
            parity=parity,
            timeout=timeout,
        )

    async def connect(self) -> bool:
        """Connect to the Modbus serial device."""
        connected = await self._client.connect()
        if connected:
            _LOGGER.debug(
                "Modbus connected on %s (slave %s)",
                self._port,
                self._slave,
            )
        else:
            _LOGGER.error("Modbus connection failed on %s", self._port)
        return connected

    async def disconnect(self) -> None:
        """Close the Modbus connection."""
        self._client.close()
        _LOGGER.debug("Modbus connection closed")

    @property
    def connected(self) -> bool:
        """Return whether the client is currently connected."""
        return self._client.connected

    async def read_input_register(self, address: int) -> int | None:
        """Read a single input register."""
        try:
            response = await self._client.read_input_registers(address, count=1)
        except Exception:
            _LOGGER.exception("read_input_register %d failed", address)
            return None

        if response.isError():
            return None
        return response.registers[0]

    async def read_input_registers(
        self,
        address: int,
        count: int,
    ) -> list[int] | None:
        """Read multiple input registers."""
        try:
            response = await self._client.read_input_registers(address, count=count)
        except Exception:
            _LOGGER.exception("read_input_registers %d failed", address)
            return None

        if response.isError():
            return None
        return response.registers

    async def read_holding_register(self, address: int) -> int | None:
        """Read a single holding register."""
        try:
            response = await self._client.read_holding_registers(address, count=1)
        except Exception:
            _LOGGER.exception("read_holding_register %d failed", address)
            return None

        if response.isError():
            return None
        return response.registers[0]

    async def write_register(self, address: int, value: int) -> bool:
        """Write a value to a holding register."""
        try:
            response = await self._client.write_register(address, value)
        except Exception:
            _LOGGER.exception("write_register %d failed", address)
            return False

        return not response.isError()

    @staticmethod
    def apply_scale(
        raw: float,
        scale: float,
        *,
        signed: bool = False,
    ) -> int | float:
        """Apply a scale factor to a raw register value."""
        if signed:
            raw = _to_signed16(int(raw))
        return raw * scale

    @staticmethod
    def extract_bit(value: int, bit: int) -> bool:
        """Extract a bit from an integer value."""
        return bool((value >> bit) & 1)

    @staticmethod
    def ascii_registers_to_string(registers: Sequence[int]) -> str:
        """Convert ASCII register values into a readable string."""
        chars: list[str] = []
        for reg in registers:
            high = (reg >> 8) & 0xFF
            low = reg & 0xFF
            if high:
                chars.append(chr(high))
            if low:
                chars.append(chr(low))
        return "".join(chars).strip()

    async def read_device_info(self) -> dict[str, str | None]:
        """Read device metadata such as firmware, model, and serial number."""
        info: dict[str, str | None] = {}
        major = await self.read_input_register(6000)
        minor = await self.read_input_register(6001)
        build = await self.read_input_register(6002)
        if major is not None and minor is not None and build is not None:
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

    logging.getLogger("custom_components.swegon_genius").warning(
        "pymodbus version: %s",
        pymodbus.__version__,
    )
except Exception:  # noqa: BLE001, S110
    pass
