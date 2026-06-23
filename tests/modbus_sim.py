#!/usr/bin/env python3
"""
Swegon CASA Genius Modbus simulator.

Serves fake but realistic register values matching registers_genius.py,
so the HA custom integration can be tested end-to-end (config flow,
entities, dashboard) without the real device.

Supports two transports:
  --mode tcp   : Modbus TCP server on 0.0.0.0:5020 (easiest in Docker)
  --mode rtu   : Modbus RTU server on a serial port (e.g. /tmp/ttyV1 from socat,
                 or a real adapter for loopback testing)

Usage:
    socat -d -d pty,raw,echo=0,link=/tmp/ttyV0 pty,raw,echo=0,link=/tmp/ttyV1
    python3 tests/modbus_sim.py --mode rtu --port /tmp/ttyV1 --baudrate 38400

Then point your HA integration's config flow at:
    TCP:  host=<container-name-or-ip>, port=5020
    RTU:  port=/tmp/ttyV0 (the OTHER end of the socat pair), baudrate=38400

Values drift slightly every update cycle to look "alive" on dashboards.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import random

from pymodbus.datastore import (
    ModbusDeviceContext,
    ModbusSequentialDataBlock,
    ModbusServerContext,
)
from pymodbus.exceptions import ModbusIOException
from pymodbus.server import StartAsyncSerialServer, StartAsyncTcpServer

try:
    from pymodbus.device import ModbusDeviceIdentification
except ImportError:
    from pymodbus.pdu.device import ModbusDeviceIdentification

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
_LOGGER = logging.getLogger("swegon_sim")

SLAVE_ID = 1
ADDRESS_BLOCK_SIZE = 10000  # registers 0..9999 covers all 3x/4x ranges we need

# ---------------------------------------------------------------------------
# Helpers: pymodbus datastore is 0-indexed and addresses passed to
# read_input_registers(address=N) map directly to this index N (no -1 offset
# needed here, since modbus_client.py in the integration already uses the
# register number as the address — keep both sides consistent).
# ---------------------------------------------------------------------------


def to_unsigned16(value: int) -> int:
    """Convert a signed int to unsigned 16-bit representation for Modbus."""
    return value & 0xFFFF


# ---------------------------------------------------------------------------
# Initial fake values — keyed by REGISTER NUMBER (matches registers_genius.py)
# ---------------------------------------------------------------------------
INITIAL_INPUT_REGISTERS: dict[int, int] = {
    # --- Device info ---
    6001: 4,  # firmware major
    6002: 3,  # firmware minor
    6003: 800,  # firmware build  -> 4.3.800
    # Model name "W5 500W A" as ASCII packed into registers 6008-6022 (15 regs)
    # Serial number block 6024-6047 (24 regs) - filled below with helper
    # --- Diagnostics - Measurements (temperatures, x0.1 °C) ---
    6201: 85,  # fresh_air_temp        = 8.5 °C
    6202: 195,  # supply_air_before_reheater = 19.5 °C
    6203: 213,  # supply_air_temp        = 21.3 °C
    6204: 222,  # extract_air_temp       = 22.2 °C
    6205: 112,  # exhaust_air_temp       = 11.2 °C
    6209: 350,  # water_radiator_temp    = 35.0 °C
    6211: 84,  # external_outside_air_temp = 8.4 °C
    6206: 215,  # room_air_temp          = 21.5 °C
    # --- CO2 / RH / VOC ---
    6213: 612,  # room_air_co2 ppm
    6214: 42,  # room_air_rh %
    6217: 180,  # room_air_voc ppm
    # --- Duct pressure / airflow ---
    6218: 85,  # supply_duct_pressure Pa
    6219: 78,  # exhaust_duct_pressure Pa
    6220: 28,  # supply_air_flow l/s
    6221: 27,  # exhaust_air_flow l/s
    # --- Unit status / fans ---
    6301: 3,  # unit_state = Normal
    6303: 65,  # supply_fan_control %
    6304: 63,  # exhaust_fan_control %
    6305: 1850,  # supply_fan_rpm
    6306: 1790,  # exhaust_fan_rpm
    6320: 18,  # effective_temp_setpoint °C (raw, NOT x0.1 per PDF note: "13-25 °C")
    6308: 0,  # boost_time_left min
    6310: 5,  # co2_automation_pct
    6311: 12,  # rh_automation_pct
    6434: 2,  # ventilation_speed_state (Genius) = Home
    # --- Alarms (all clear by default) ---
    6132: 0,  # active_alarms_flag
    6195: 0,  # critical_alarms_flag
    6136: 0,  # active_alarms_word1 bitmask
    6191: 0,  # active_alarms_word2 bitmask
    6193: 0,  # active_alarms_word3 bitmask
}

INITIAL_HOLDING_REGISTERS: dict[int, int] = {
    5001: 2,  # operation_mode write = Home
    5009: 1,  # co2_automation switch = on
    5010: 2,  # rh_automation level = Normal
    5018: 0,  # emergency_stop = disabled
    5101: 180,  # temperature_setpoint raw = 18.0 °C (x10 per PDF: 130-250 = 13.0-25.0°C)
}


def pack_ascii(text: str, num_registers: int) -> list[int]:
    """Pack an ASCII string into Modbus registers, 2 chars per register (big-endian)."""
    data = text.encode("ascii")
    data = data.ljust(num_registers * 2, b"\x00")
    regs = []
    for i in range(0, num_registers * 2, 2):
        regs.append((data[i] << 8) | data[i + 1])
    return regs


def build_datastore() -> tuple[ModbusServerContext, ModbusDeviceContext]:
    """Build the simulated Modbus datastore with fake Swegon register values."""

    input_block = [0] * ADDRESS_BLOCK_SIZE
    holding_block = [0] * ADDRESS_BLOCK_SIZE

    for addr, value in INITIAL_INPUT_REGISTERS.items():
        input_block[addr] = to_unsigned16(value)

    for addr, value in INITIAL_HOLDING_REGISTERS.items():
        holding_block[addr] = to_unsigned16(value)

    # Model name (3x6008, 15 registers) -> "W5 500W A"
    model_regs = pack_ascii("W5 500W A", 15)
    for i, val in enumerate(model_regs):
        input_block[6008 + i] = val

    # Serial number (3x6024, 24 registers) -> fake serial
    serial_regs = pack_ascii("SIM-2026-000123456789", 24)
    for i, val in enumerate(serial_regs):
        input_block[6024 + i] = val

    # pymodbus uses 0-based addressing: ModbusSequentialDataBlock(0, values) means
    # values[0] is read by client read_*_registers(address=0). Since modbus_client.py
    # passes the raw SCB 4.1 register number directly as the address, our datastore
    # arrays are pre-sized to ADDRESS_BLOCK_SIZE and indexed by that same register
    # number — no offset needed on either side.
    store = ModbusDeviceContext(
        di=ModbusSequentialDataBlock(0, [0] * ADDRESS_BLOCK_SIZE),
        co=ModbusSequentialDataBlock(0, [0] * ADDRESS_BLOCK_SIZE),
        hr=ModbusSequentialDataBlock(0, holding_block),
        ir=ModbusSequentialDataBlock(0, input_block),
    )

    context = ModbusServerContext(devices=store, single=True)
    return context, store


# ---------------------------------------------------------------------------
# Background task: drift sensor values slightly every few seconds so the
# HA dashboard looks "alive" rather than static.
# ---------------------------------------------------------------------------

DRIFT_REGISTERS = {
    6201: (-100, 250, 1),  # fresh_air_temp range -10.0..25.0 °C, step granularity
    6203: (150, 220, 1),  # supply_air_temp
    6204: (180, 250, 1),  # extract_air_temp
    6206: (180, 250, 1),  # room_air_temp
    6213: (450, 1200, 5),  # room_air_co2 ppm
    6214: (30, 60, 1),  # room_air_rh %
    6305: (1500, 2200, 10),  # supply_fan_rpm
    6306: (1450, 2150, 10),  # exhaust_fan_rpm
}


async def drift_values(store: ModbusDeviceContext, interval: float = 5.0) -> None:
    """Periodically nudge a few registers to simulate a live device."""
    while True:
        await asyncio.sleep(interval)
        for addr, (lo, hi, step) in DRIFT_REGISTERS.items():
            current_values = store.getValues(
                4, addr, count=1
            )  # fc=4 -> input registers
            if not isinstance(current_values, (list, tuple)) or not current_values:
                continue
            current = current_values[0]
            # unsigned -> signed for temps that can be negative
            signed = current - 65536 if current > 32767 else current
            delta = random.choice([-step, 0, step])
            new_val = max(lo, min(hi, signed + delta))
            store.setValues(4, addr, [to_unsigned16(new_val)])
        _LOGGER.debug("Drifted simulated sensor values")


MODE_READ_MAP = {
    0: 0,
    1: 2,
    2: 3,
    3: 5,
    4: 1,
    5: 4,
}

async def operation_mode_reg(store: ModbusDeviceContext, interval: float = 1.0) -> None:
    """Mirror operation mode from holding register 5001 to input register 6434."""
    while True:
        await asyncio.sleep(interval)
        try:
            mode_values = store.getValues(3, 5001, count=1)  # fc=3 -> holding registers
            if not isinstance(mode_values, (list, tuple)) or not mode_values:
                continue
            mode = mode_values[0]
            mapped_mode = MODE_READ_MAP.get(mode)
            if mapped_mode is None:
                _LOGGER.debug("Unsupported operation mode write value: %s", mode)
                continue
            store.setValues(
                4, 6434, [to_unsigned16(mapped_mode)]
            )  # fc=4 -> input registers
        except ModbusIOException as exc:
            _LOGGER.debug(
                "Transient Modbus error while mirroring operation mode: %s", exc
            )


# ---------------------------------------------------------------------------
# Identification (shown to clients that query device identification objects)
# ---------------------------------------------------------------------------


def build_identity() -> ModbusDeviceIdentification:
    identity = ModbusDeviceIdentification()
    identity.VendorName = "Swegon (SIMULATED)"
    identity.ProductCode = "CASA-GENIUS-SIM"
    identity.VendorUrl = "https://www.swegon.com"
    identity.ProductName = "CASA Genius W5 500W A (Simulator)"
    identity.ModelName = "W5 500W A"
    identity.MajorMinorRevision = "4.3.800"
    return identity


# ---------------------------------------------------------------------------
# Entrypoints
# ---------------------------------------------------------------------------


async def run_tcp(host: str, port: int) -> None:
    context, store = build_datastore()
    identity = build_identity()
    asyncio.create_task(drift_values(store))
    asyncio.create_task(operation_mode_reg(store))
    _LOGGER.info(
        "Starting Swegon GENIUS Modbus TCP simulator on %s:%s (slave id=%s)",
        host,
        port,
        SLAVE_ID,
    )
    await StartAsyncTcpServer(context=context, identity=identity, address=(host, port))


async def run_rtu(serial_port: str, baudrate: int) -> None:
    context, store = build_datastore()
    identity = build_identity()
    asyncio.create_task(drift_values(store))
    asyncio.create_task(operation_mode_reg(store))
    _LOGGER.info(
        "Starting Swegon GENIUS Modbus RTU simulator on %s @ %s baud (slave id=%s)",
        serial_port,
        baudrate,
        SLAVE_ID,
    )
    try:
        await StartAsyncSerialServer(
            context=context,
            identity=identity,
            port=serial_port,
            baudrate=baudrate,
            bytesize=8,
            parity="N",
            stopbits=1,
            timeout=1,
        )
    except Exception as exc:
        import traceback

        traceback.print_exc()
        print(exc)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Swegon CASA Genius Modbus simulator")
    parser.add_argument("--mode", choices=["tcp", "rtu"], default="tcp")
    parser.add_argument("--host", default="0.0.0.0", help="TCP bind host (mode=tcp)")
    parser.add_argument(
        "--tcp-port", type=int, default=5020, help="TCP port (mode=tcp)"
    )
    parser.add_argument("--port", default="/tmp/ttyV1", help="Serial port (mode=rtu)")
    parser.add_argument(
        "--baudrate", type=int, default=38400, help="Baudrate (mode=rtu)"
    )
    args = parser.parse_args()

    # logging.getLogger("pymodbus").setLevel(logging.DEBUG)

    if args.mode == "tcp":
        asyncio.run(run_tcp(args.host, args.tcp_port))
    else:
        asyncio.run(run_rtu(args.port, args.baudrate))


if __name__ == "__main__":
    main()
