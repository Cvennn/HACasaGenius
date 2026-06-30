"""Constants for Swegon GENIUS integration."""

DOMAIN = "swegon_genius"

# Config entry keys
CONF_PORT = "port"
CONF_SLAVE = "slave"
CONF_BAUDRATE = "baudrate"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_PARITY = "parity"
CONF_STOPBITS = "stopbits"

# Defaults
DEFAULT_SLAVE = 1
DEFAULT_BAUDRATE = 38400
DEFAULT_SCAN_INTERVAL = 30  # seconds
DEFAULT_PORT = "/dev/ttyUSB0"
DEFAULT_PARITY = "N"
DEFAULT_BYTESIZE = 8
DEFAULT_TIMEOUT = 5
DEFAULT_STOPBITS = 1

# Modbus register types
REG_INPUT = "input"  # 3x — read only (input registers)
REG_HOLDING = "holding"  # 4x — read/write (holding registers)

# Operation mode WRITE values (register 4x5001)
# NOTE: read state uses 3x6434 which has DIFFERENT numbering — see registers_genius.py
OPERATION_MODES_WRITE = {
    0: "off",
    1: "away",
    2: "home",
    3: "boost",
    4: "travel",
    5: "home_plus",
}

# Operation mode READ states (register 3x6434 — Genius)
OPERATION_MODES_READ = {
    0: "off",
    1: "travel",
    2: "away",
    3: "home",
    4: "home_plus",
    5: "boost",
    6: "fireplace",
}

# Map: aktiivinen ventilointitila (3x6434) -> käyttötilan nimi (select-näyttö)
VENTILATION_TO_MODE = {
    0: "off",
    1: "travel",
    2: "away",
    3: "home",
    4: "home_plus",
    5: "boost",
    6: "home",  # Fireplace active -> display Home
}

# RH automation levels (register 4x5010)
RH_LEVELS = {
    0: "off",
    1: "low",
    2: "normal",
    3: "high",
    4: "max",
    5: "advanced"
}

# VOC-automaatiotasot — 4x5011
VOC_AUTOMATION_LEVELS = {
    0: "off",
    1: "low",
    2: "normal",
    3: "high",
    4: "max",
    5: "advanced"
}

# Kesätilan boost — 4x5169
SUMMER_BOOST_LEVELS = {
    0: "off",
    1: "low",
    2: "normal",
    3: "high",
    4: "max",
    5: "advanced"
}

# Boost-ajastin — 4x5102
BOOST_TIMER_OPTIONS = {
    0: "continuous",
    1: "30",
    2: "60",
    3: "90",
    4: "120",
    5: "240"
}

# Hätäpysäytys — 4x5018
EMERGENCY_STOP_OPTIONS = {
    0: "offline",
    1: "emergency_stop",
    2: "overpressure"
}

# Takkatoiminnon taso — 4x5105
FIREPLACE_LEVELS = {
    0: "low",
    1: "normal",
    2: "high"
}

# Yksikön tila — 3x6301
UNIT_STATES = {
    0: "Kriittinen pysäytys",
    1: "Käyttäjä pysäyttänyt",
    2: "Käynnistyy",
    3: "Normaali",
    4: "Käyttöönotto",
}

# Lämmitystila — 3x6370
HEATING_STATES = {
    0: "Käynnistyy",
    1: "Pysäytetty",
    2: "Ulkoinen jäähdytys",
    3: "Sisäinen jäähdytys",
    4: "Sisäinen jäähdytys (rajoitettu)",
    5: "Kesätila",
    6: "LTO-ohjaus",
    7: "Lämmitys",
    8: "Sulatus 1",
    9: "Sulatus 2",
    10: "Sulatus 3",
}

# Temperature setpoint limits (register 4x5101)
TEMP_SETPOINT_MIN = 13.0
TEMP_SETPOINT_MAX = 25.0
TEMP_SETPOINT_STEP = 0.5
