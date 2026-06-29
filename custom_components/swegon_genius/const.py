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
    0: "Sammutettu",
    1: "Poissa",
    2: "Kotona",
    3: "Tehostus",
    4: "Matkoilla",
    5: "Kotona+",
}

# Operation mode READ states (register 3x6434 — Genius)
OPERATION_MODES_READ = {
    0: "Pysäytetty",
    1: "Matkoilla",
    2: "Poissa",
    3: "Kotona",
    4: "Kotona+",
    5: "Tehostus",
    6: "Takkatoiminto",
}

# Map: aktiivinen ventilointitila (3x6434) -> käyttötilan nimi (select-näyttö)
VENTILATION_TO_MODE = {
    0: "Sammutettu",
    1: "Matkoilla",
    2: "Poissa",
    3: "Kotona",
    4: "Kotona+",
    5: "Tehostus",
    6: "Kotona",  # takka päällä — näytetään perustila
}

# RH automation levels (register 4x5010)
RH_LEVELS = {
    0: "Pois",
    1: "Matala",
    2: "Normaali",
    3: "Korkea",
    4: "Maksimi",
    5: "Edistynyt",
}

# VOC-automaatiotasot — 4x5011
VOC_AUTOMATION_LEVELS = {
    0: "Pois",
    1: "Matala",
    2: "Normaali",
    3: "Korkea",
    4: "Maksimi",
    5: "Edistynyt",
}

# Kesätilan boost — 4x5169
SUMMER_BOOST_LEVELS = {
    0: "Pois",
    1: "Matala",
    2: "Normaali",
    3: "Korkea",
    4: "Maksimi",
    5: "Edistynyt",
}

# Boost-ajastin — 4x5102
BOOST_TIMER_OPTIONS = {
    0: "Jatkuva",
    1: "30 min",
    2: "60 min",
    3: "90 min",
    4: "120 min",
    5: "240 min",
}

# Hätäpysäytys — 4x5018
EMERGENCY_STOP_OPTIONS = {
    0: "Pois käytöstä",
    1: "Hätäpysäytys",
    2: "Ylipaineistus",
}

# Takkatoiminnon taso — 4x5105
FIREPLACE_LEVELS = {
    0: "Matala",
    1: "Normaali",
    2: "Korkea",
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
