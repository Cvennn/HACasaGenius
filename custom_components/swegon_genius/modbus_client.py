import logging
from typing import Any
from pymodbus.client import AsyncModbusSerialClient
from pymodbus.exceptions import ModbusException

_LOGGER = logging.getLogger(__name__)

class CasaGeniusModbusClient:

    def __init__(
        self,
        port: str,
        slave: int,
        baudrate: int 38400,) -> None:
        self._port = port,
        self._slave = slave,
        self._client = AsyncModbusSerialClient(
            port = port,
            baudrate = baudrate,
            bytesize = 8,
            parity = "N",
            stopbits = 1,
        )

    async def connect(self) -> bool:
        connected = await self._client.connect()
        if connected:
            _LOGGER.debug("Modbus connected %s (slave %s)", self.port, self._slave)
        else:
            _LOGGER.debug("Modbus connection fail %s", self.port)
        return connected


    async def close(self) -> None:
        self._client.close()
        _LOGGER.debug("Modbus connection closed")

    @property
    def connectef(self) -> bool:
        return self._client.connected

    async def read_input_register(self, address: int, count: int 1) -> list[int] | None:
        try:
            result = await self._client.read_input_registers(address = address, count = count, slave = self._slave)
            if result.isError():
                _LOGGER.warning("Error reading input register %s count=%s %s", address, count, result)
                return None
            return result.registers
        except ModbusException as err:
            _LOGGER.error("Modbus exception reading register %s: %s", address, err)
            return None


    # async def read_holding_register


    # async def write_holding_register


    # async def read_single_input

    # async def read_single_holding