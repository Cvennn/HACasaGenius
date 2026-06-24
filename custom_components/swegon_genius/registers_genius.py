"""Swegon CASA Genius SCB 4.1 Modbus register definitions."""

from __future__ import annotations

from .const import REG_HOLDING, REG_INPUT

# DEVICE INFORMATION — 3x6001–3x6024 (read on setup, not polled every cycle)
DEVICE_INFO_REGISTERS: dict[str, dict] = {
    "firmware_major": {
        "address": 6001,
        "type": REG_INPUT,
        "name": "Firmware Version Major",
    },
    "firmware_minor": {
        "address": 6002,
        "type": REG_INPUT,
        "name": "Firmware Version Minor",
    },
    "firmware_build": {
        "address": 6003,
        "type": REG_INPUT,
        "name": "Firmware Build",
    },
    # Model name: 15 registers ASCII (3x6008–3x6022), read as block
    "model_name_start": {
        "address": 6008,
        "type": REG_INPUT,
        "count": 15,  # read 15 registers at once
        "name": "Model Name",
    },
    # Serial number: 24 registers ASCII (3x6024–3x6047), read as block
    "serial_number_start": {
        "address": 6024,
        "type": REG_INPUT,
        "count": 24,
        "name": "Unit Serial Number",
    },
}

# SENSOR registers — 3x input registers, Diagnostics-Measurements section
# Scale applied in coordinator. Temperatures: ×0.1°C, signed 16-bit.
SENSOR_REGISTERS: dict[str, dict] = {
    # --- Air temperatures (Diagnostics - Measurements, page 6) ---
    "fresh_air_temp": {
        "address": 6201,
        "type": REG_INPUT,
        "scale": 0.1,
        "unit": "°C",
        "device_class": "temperature",
        "state_class": "measurement",
        "name": "Fresh Air Temperature",
    },
    "supply_air_before_reheater_temp": {
        "address": 6202,
        "type": REG_INPUT,
        "scale": 0.1,
        "unit": "°C",
        "device_class": "temperature",
        "state_class": "measurement",
        "name": "Supply Air Before Re-heater Temperature",
    },
    "supply_air_temp": {
        "address": 6203,
        "type": REG_INPUT,
        "scale": 0.1,
        "unit": "°C",
        "device_class": "temperature",
        "state_class": "measurement",
        "name": "Supply Air Temperature",
    },
    "extract_air_temp": {
        "address": 6204,
        "type": REG_INPUT,
        "scale": 0.1,
        "unit": "°C",
        "device_class": "temperature",
        "state_class": "measurement",
        "name": "Extract Air Temperature",
    },
    "exhaust_air_temp": {
        "address": 6205,
        "type": REG_INPUT,
        "scale": 0.1,
        "unit": "°C",
        "device_class": "temperature",
        "state_class": "measurement",
        "name": "Exhaust Air Temperature",
    },
    "water_radiator_temp": {
        "address": 6209,
        "type": REG_INPUT,
        "scale": 0.1,
        "unit": "°C",
        "device_class": "temperature",
        "state_class": "measurement",
        "name": "Water Radiator Temperature",
    },
    "external_outside_air_temp": {
        "address": 6211,
        "type": REG_INPUT,
        "scale": 0.1,
        "unit": "°C",
        "device_class": "temperature",
        "state_class": "measurement",
        "name": "External Outside Air Temperature",
    },
    "room_air_temp": {
        "address": 6206,
        "type": REG_INPUT,
        "scale": 0.1,
        "unit": "°C",
        "device_class": "temperature",
        "state_class": "measurement",
        "name": "Room Air Temperature",
   },
    # --- CO2 ---
    "room_air_co2": {
        "address": 6213,
        "type": REG_INPUT,
        "scale": 1,
        "unit": "ppm",
        "device_class": "carbon_dioxide",
        "state_class": "measurement",
        "name": "Room Air CO2",
    },
    # --- Humidity ---
    "room_air_rh": {
        "address": 6214,
        "type": REG_INPUT,
        "scale": 1,
        "unit": "%",
        "device_class": "humidity",
        "state_class": "measurement",
        "name": "Room Air Relative Humidity",
    },
    # --- VOC ---
    "room_air_voc": {
        "address": 6217,
        "type": REG_INPUT,
        "scale": 1,
        "unit": "ppm",
        "device_class": None,
        "state_class": "measurement",
        "name": "Room Air VOC",
    },
    # --- Airflow / Pressure ---
    "supply_duct_pressure": {
        "address": 6218,
        "type": REG_INPUT,
        "scale": 1,
        "unit": "Pa",
        "device_class": "pressure",
        "state_class": "measurement",
        "name": "Supply Duct Pressure",
    },
    "exhaust_duct_pressure": {
        "address": 6219,
        "type": REG_INPUT,
        "scale": 1,
        "unit": "Pa",
        "device_class": "pressure",
        "state_class": "measurement",
        "name": "Exhaust Duct Pressure",
    },
    "supply_air_flow": {
        "address": 6220,
        "type": REG_INPUT,
        "scale": 1,
        "unit": "l/s",
        "device_class": None,
        "state_class": "measurement",
        "name": "Supply Air Flow",
    },
    "exhaust_air_flow": {
        "address": 6221,
        "type": REG_INPUT,
        "scale": 1,
        "unit": "l/s",
        "device_class": None,
        "state_class": "measurement",
        "name": "Exhaust Air Flow",
    },
    # --- Unit Status / Fan (Diagnostics - Unit Status, page 7) ---
    "supply_fan_control": {
        "address": 6303,
        "type": REG_INPUT,
        "scale": 1,
        "unit": "%",
        "device_class": None,
        "state_class": "measurement",
        "name": "Supply Fan Control",
    },
    "exhaust_fan_control": {
        "address": 6304,
        "type": REG_INPUT,
        "scale": 1,
        "unit": "%",
        "device_class": None,
        "state_class": "measurement",
        "name": "Exhaust Fan Control",
    },
    "supply_fan_rpm": {
        "address": 6305,
        "type": REG_INPUT,
        "scale": 1,
        "unit": "rpm",
        "device_class": None,
        "state_class": "measurement",
        "name": "Supply Fan RPM",
    },
    "exhaust_fan_rpm": {
        "address": 6306,
        "type": REG_INPUT,
        "scale": 1,
        "unit": "rpm",
        "device_class": None,
        "state_class": "measurement",
        "name": "Exhaust Fan RPM",
    },
    "effective_temp_setpoint": {
        "address": 6320,
        "type": REG_INPUT,
        "scale": 1,
        "unit": "°C",
        "device_class": "temperature",
        "state_class": "measurement",
        "name": "Effective Temperature Setpoint",
    },
    # --- Automation contributions ---
    "co2_automation_pct": {
        "address": 6310,
        "type": REG_INPUT,
        "scale": 1,
        "unit": "%",
        "device_class": None,
        "state_class": "measurement",
        "name": "CO2 Automation Fan Change",
    },
    "rh_automation_pct": {
        "address": 6311,
        "type": REG_INPUT,
        "scale": 1,
        "unit": "%",
        "device_class": None,
        "state_class": "measurement",
        "name": "RH Automation Fan Boost",
    },
}


ALARM_REGISTERS: dict[str, dict] = {
    "active_alarms_word1": {
        "address": 6136,
        "type": REG_INPUT,
        "name": "Active Alarms Word 1",
        # Bit 0 = LSB
        "bits": {
            0: ("E011", "Postheater failure"),
            1: ("E021", "Preheater failure"),
            2: ("RSVD", "Reserved"),
            3: ("E041", "Freezing danger"),
            4: ("E051", "Supply fan failure"),
            5: ("E061", "Exhaust fan failure"),
            6: ("E15x", "Temperature sensor failure (T1–T9)"),
            7: ("E071", "Emergency stop active"),
            8: ("RSVD", "Reserved"),
            9: ("INFO", "Service info"),
            10: ("GENIUS", "New Genius alarm"),
            11: ("E111", "Supply temperature low alarm"),
            12: ("E121", "Internal temperature high alarm"),
            13: ("PREHEAT", "Preheater temperature high alarm"),
            14: ("E131", "Rotor RPM alarm"),
            15: ("FANCTRL", "Fan control alarm"),
        },
    },
    "active_alarms_word2": {
        "address": 6191,
        "type": REG_INPUT,
        "name": "Active Alarms Word 2",
        "bits": {
            0: ("E171", "Sensor package failure"),
            1: ("E172", "RH sensor failure"),
            2: ("E173", "CO2 sensor failure"),
            3: ("E174", "VOC sensor failure"),
            4: ("E031", "External electrical preheater failure"),
            5: ("E181", "External electrical postheater failure"),
            6: ("E071b", "Internal PCB temperature high"),
            7: ("PARAM", "Internal parameter error"),
            8: ("E091", "External alarm"),
            9: ("E093", "External device message"),
            10: ("E092", "External critical alarm"),
            11: ("E101", "External fire detector alarm"),
            12: ("E141", "Heat exchanger efficiency low"),
            13: ("HEXCTRL", "Heat exchanger control failure"),
        },
    },
    "active_alarms_word3": {
        "address": 6193,
        "type": REG_INPUT,
        "name": "Active Alarms Word 3",
        "bits": {
            0: ("E191", "Cooling condenser temperature high"),
            1: ("E192", "Cooling hotgas temperature high"),
            2: ("E193", "Cooling pressure high"),
            3: ("E134", "Rotor stall detection"),
            4: ("E133", "Rotor driver overheat"),
            5: ("E132", "Rotor connection failure"),
            6: ("E502", "Indoor humidity alarm"),  # SCB 4.1+
            7: ("E512", "Cooling coil condense removal critical failure"),  # SCB 4.1+
        },
    },
}

# Additional binary status registers (single-bit, not bitmask)
STATUS_BINARY_REGISTERS: dict[str, dict] = {
    "active_alarms_flag": {
        "address": 6132,
        "type": REG_INPUT,
        "name": "Active Alarms",
        "device_class": "problem",
        "note": "0 = No alarms, 1 = Active alarm",
    },
    "critical_alarms_flag": {
        "address": 6195,
        "type": REG_INPUT,
        "name": "Critical Alarms (Ventilation Stopped)",
        "device_class": "problem",
        "note": "Only in Genius control system (SW4.0+)",
    },
}

# SELECT registers
# IMPORTANT: Operating mode write → 4x5001, read active state → 3x6434
#            3x6434 has MORE states than 4x5001 (adds Fireplace state)
SELECT_REGISTERS: dict[str, dict] = {
    "operation_mode": {
        "write_address": 5001,
        "write_type": REG_HOLDING,
        "read_address": 6434,
        "read_type": REG_INPUT,
        "name": "Operation Mode",
        "icon": "mdi:air-filter",
        "write_options": {
            0: "Shutdown",
            1: "Away",
            2: "Home",
            3: "Boost",
            4: "Travelling",
            5: "Home+",
        },
        "read_states": {
            0: "Stopped",
            1: "Travelling",
            2: "Away",
            3: "Home",
            4: "Home+",
            5: "Boost",
            6: "Fireplace",
        },
    },
    "rh_automation": {
        "write_address": 5010,
        "write_type": REG_HOLDING,
        "read_address": 5010,
        "read_type": REG_HOLDING,
        "name": "RH Automation Level",
        "icon": "mdi:water-percent",
        "write_options": {
            0: "Off",
            1: "Low",
            2: "Normal",
            3: "High",
            4: "Max",
            5: "Advanced",
        },
        "read_states": {
            0: "Off",
            1: "Low",
            2: "Normal",
            3: "High",
            4: "Max",
            5: "Advanced",
        },
    },
    "cooker_hood_mode": {
        "write_address": 5020,
        "write_type": REG_HOLDING,
        "read_address": 5020,
        "read_type": REG_HOLDING,
        "name": "Cooker Hood Mode",
        "icon": "mdi:stove",
        "write_options": {
            0: "No Cooker Hood",
            1: "Hood with Ventilation Unit",
            2: "Hood with Roof Fan",
            3: "Hood with Integrated Fan",
            4: "Recirculating Cooker Hood",
        },
        "read_states": {
            0: "No Cooker Hood",
            1: "Hood with Ventilation Unit",
            2: "Hood with Roof Fan",
            3: "Hood with Integrated Fan",
            4: "Recirculating Cooker Hood",
        },
        "note": "Different from cooking mode activation (4x5005). Sets cooker hood type.",
    },
}

# NUMBER registers — temperature setpoint, fireplace level
# 4x5101: Supply temperature setpoint, range 130–250 (×0.1°C = 13.0–25.0°C)
# Write: send value × 10 (integer). Read: raw × 0.1 → °C.
NUMBER_REGISTERS: dict[str, dict] = {
    "temperature_setpoint": {
        "address": 5101,  # 4x5101
        "type": REG_HOLDING,
        "name": "Temperature Setpoint",
        "unit": "°C",
        "device_class": "temperature",
        "min": 13.0,
        "max": 25.0,
        "step": 0.5,
        "scale": 0.1,
        "write_scale": 10,
        "raw_min": 130,
        "raw_max": 250,
    },
    "fireplace_level": {
        "address": 5105,
        "type": REG_HOLDING,
        "name": "Fireplace Level",
        "unit": "",
        "device_class": None,
        "min": 0,
        "max": 2,
        "step": 1,
        "scale": 1,
    },
}

# SWITCH registers — true on/off holding registers
SWITCH_REGISTERS: dict[str, dict] = {
    "co2_automation": {
        "address": 5009,
        "type": REG_HOLDING,
        "name": "CO2 Automation",
        "icon": "mdi:molecule-co2",
        "note": "0=Auto Home/Away/Boost control disabled, 1=enabled. Available only in units with CO2 sensor.",
    },
    "emergency_stop": {
        "address": 5018,
        "type": REG_HOLDING,
        "name": "Emergency Stop",
        "icon": "mdi:stop-circle-outline",
        "device_class": "switch",
    },
    "cooking_mode": {
        "address": 5005,
        "type": REG_HOLDING,
        "name": "Cooking Mode",
        "icon": "mdi:pot-mix",
        "device_class": "switch",
    },
    "fireplace_mode": {
        "address": 5002,
        "type": REG_HOLDING,
        "name": "Fireplace Mode",
        "icon": "mdi:fireplace",
        "device_class": "switch",
    },
}

# UNIT STATUS registers — read-only
UNIT_STATUS_REGISTERS: dict[str, dict] = {
    "unit_state": {
        "address": 6301,
        "type": REG_INPUT,
        "name": "Unit State",
        "states": {
            0: "Critical Stop",
            1: "User Stopped",
            2: "Starting",
            3: "Normal",
            4: "Commissioning",
        },
    },
    "ventilation_speed_state": {
        "address": 6434,
        "type": REG_INPUT,
        "name": "Ventilation Speed State",
        "states": {
            0: "Stopped",
            1: "Travelling",
            2: "Away",
            3: "Home",
            4: "Home+",
            5: "Boost",
            6: "Fireplace",
        },
    },
    "boost_time_left": {
        "address": 6308,
        "type": REG_INPUT,
        "scale": 1,
        "unit": "min",
        "device_class": None,
        "name": "Boost Time Left",
    },
    "temperature_setpoint_active": {
        "address": 6320,
        "type": REG_INPUT,
        "scale": 0.1,
        "unit": "°C",
        "device_class": "temperature",
        "state_class": "measurement",
        "name": "Active Temperature Setpoint",
    },
    "fireplace_function_active": {
        "address": 6335,
        "type": REG_INPUT,
        "name": "Fireplace Function Active",
        "icon": "mdi:fireplace",
        "device_class": "binary_sensor",
        "states": {
            0: "Inactive",
            1: "Active",
        },
    },
    "cooking_mode_active": {
        "address": 6337,
        "type": REG_INPUT,
        "name": "Cooking Mode Active",
        "icon": "mdi:pot-mix",
        "device_class": "binary_sensor",
        "states": {
            0: "Inactive",
            1: "Active",
        },
    },
}
