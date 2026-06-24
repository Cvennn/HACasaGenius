"""Constants for Swegon GENIUS integration."""

DOMAIN = "swegon_genius"

# Config entry keys
CONF_PORT = "port"
CONF_SLAVE = "slave"
CONF_BAUDRATE = "baudrate"
CONF_SCAN_INTERVAL = "scan_interval"

# Defaults
DEFAULT_SLAVE = 1
DEFAULT_BAUDRATE = 38400
DEFAULT_SCAN_INTERVAL = 30  # seconds
DEFAULT_PORT = "/dev/ttyUSB0"

# Modbus register types
REG_INPUT = "input"  # 3x — read only (input registers)
REG_HOLDING = "holding"  # 4x — read/write (holding registers)

# Operation mode WRITE values (register 4x5001)
# NOTE: read state uses 3x6434 which has DIFFERENT numbering — see registers_genius.py
OPERATION_MODES_WRITE = {
    0: "Shutdown",
    1: "Away",
    2: "Home",
    3: "Boost",
    4: "Travelling",
    5: "Home+",  # SW4.0 Genius only
}

# Operation mode READ states (register 3x6434 — Genius)
OPERATION_MODES_READ = {
    0: "Stopped",
    1: "Travelling",
    2: "Away",
    3: "Home",
    4: "Home+",
    5: "Boost",
    6: "Fireplace",
}

# RH automation levels (register 4x5010)
RH_LEVELS = {
    0: "Off",
    1: "Low",
    2: "Normal",
    3: "High",
    4: "Max",
    5: "Advanced",
}

# Temperature setpoint limits (register 4x5101)
TEMP_SETPOINT_MIN = 13.0
TEMP_SETPOINT_MAX = 25.0
TEMP_SETPOINT_STEP = 0.5
