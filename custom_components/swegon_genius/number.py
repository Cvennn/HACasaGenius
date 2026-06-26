"""
Number platform for CASA Genius.

Exposes temperature setpoint as a number entity.
SCB 4.1 register 4x5101:
  Range:  130–250 (raw Modbus integer)
  Scale:  ÷10 for display  → 13.0–25.0 °C
  Step:   0.5 °C  (raw step = 5)
  Write:  °C value × 10 → integer sent to Modbus
"""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

NUMBER_DEFS = [
{"key": "temp_setpoint",        "name": "Lampotilasetpiste",                "address": 5100,"min": 13.0,"max": 25.0,"step": 0.5,"unit": "C","scale": 0.1,},
{"key": "temp_setpoint_summer", "name": "Kesakauden lampotilasetpiste",     "address": 5167,"min": 13.0,"max": 25.0,"step": 0.5,"unit": "C","scale": 0.1,},
{"key": "temp_setpoint_away",   "name": "Away-tilan lampotilasetpiste",     "address": 5170,"min": 13.0,"max": 25.0,"step": 0.5,"unit": "C","scale": 0.1,},
{"key": "room_temp_setpoint",   "name": "Huonelampotilan asetus",           "address": 5186,"min": 16.0,"max": 26.0,"step": 0.5,"unit": "C","scale": 0.1,},
{"key": "co2_boost_limit",      "name": "CO2 Boost-raja",                   "address": 5115,"min": 0,"max": 2000,"step": 50,"unit": "ppm","scale": 1.0,},
{"key": "co2_home_limit",       "name": "CO2 Home-raja",                    "address": 5113,"min": 0,"max": 2000,"step": 50,"unit": "ppm","scale": 1.0,},
{"key": "co2_away_limit",       "name": "CO2 Away-raja",                    "address": 5114,"min": 0,"max": 2000,"step": 50,"unit": "ppm","scale": 1.0,},
{"key": "home_plus_level",      "name": "Home+ ventilointitaso",            "address": 5107,"min": 10,"max": 90,"step": 5,"unit": "%","scale": 1.0,},
{"key": "away_supply_fan",      "name": "Away-tilan tuloilmapuhallin",      "address": 5301,"min": 20,"max": 100,"step": 1,"unit": "%","scale": 1.0,},
{"key": "away_exhaust_fan",     "name": "Away-tilan poistoilmapuhallin",    "address": 5302,"min": 20,"max": 100,"step": 1,"unit": "%","scale": 1.0,},
{"key": "home_supply_fan",      "name": "Home-tilan tuloilmapuhallin",      "address": 5303,"min": 20,"max": 100,"step": 1,"unit": "%","scale": 1.0,},
{"key": "home_exhaust_fan",     "name": "Home-tilan poistoilmapuhallin",    "address": 5304,"min": 20,"max": 100,"step": 1,"unit": "%","scale": 1.0,},
{"key": "boost_supply_fan",     "name": "Boost-tilan tuloilmapuhallin",     "address": 5305,"min": 20,"max": 100,"step": 1,"unit": "%","scale": 1.0,},
{"key": "boost_exhaust_fan",    "name": "Boost-tilan poistoilmapuhallin",   "address": 5306,"min": 20,"max": 100,"step": 1,"unit": "%","scale": 1.0,},
{"key": "cooking_supply_fan",   "name": "Ruoanlaitto tuloilmapuhallin",     "address": 5183,"min": 20,"max": 100,"step": 1,"unit": "%","scale": 1.0,},
{"key": "cooking_exhaust_fan",  "name": "Ruoanlaitto poistoilmapuhallin",   "address": 5184,"min": 20,"max": 100,"step": 1,"unit": "%","scale": 1.0,},
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities
    ):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SwegonNumber(coordinator, entry, d) for d in NUMBER_DEFS])


class SwegonNumber(CoordinatorEntity, NumberEntity):
    def __init__(self, coordinator, entry, number_def):
        super().__init__(coordinator)
        self._def = number_def
        self._attr_unique_id = f"{entry.entry_id}_{number_def['key']}"
        self._attr_name = number_def["name"]
        self._attr_native_min_value = number_def["min"]
        self._attr_native_max_value = number_def["max"]
        self._attr_native_step = number_def["step"]
        self._attr_native_unit_of_measurement = number_def["unit"]
        self._attr_mode = NumberMode.BOX
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Swegon",
            model=coordinator.device_info_data.get("model", "CASA Genius"),
            sw_version=coordinator.device_info_data.get("firmware"),
        )

    @property
    def native_value(self):
        return self.coordinator.data.get(self._def["key"])

    async def async_set_native_value(self, value: float):
        scale = self._def.get("scale", 1.0)
        raw = int(round(value / scale)) if scale != 1.0 else int(value)
        await self.coordinator.client.write_register(self._def["address"], raw)
        await self.coordinator.async_request_refresh()