**Languages:** [English](README.md) | [Suomi](README.fi.md) | [Svenska](README.sv.md) | [Norsk](README.no.md)

# Swegon CASA Genius — Home Assistant integration

Home Assistant custom component for the Swegon CASA Genius ventilation unit.
Reads and controls the unit over Modbus RTU (RS485). ~121 entities:
temperatures, airflows, operating mode, alarms, settings.

> **This is a test version.** Installation is manual (not yet available via HACS).

---

## Requirements

Before you start, you'll need:

- A **Swegon CASA Genius** unit with an **SCB 4.2** control board and **SW 4.0 or newer** firmware
  (tested on a W5 500W A unit, firmware 4.3.800)
- An **RS485-USB adapter** connected to the unit's Modbus bus and to the Home Assistant server
  (e.g. a CH341-based adapter, usually shows up as `/dev/ttyUSB0`)
- Home Assistant with access to the `custom_components` folder (e.g. via Studio Code Server,
  Samba, or File Editor)

Without the physical unit and a working RS485 connection, the integration won't connect to anything.

Alternative RS485 converters:
- https://raspberrypi.dk/en/product/industrial-usb-to-rs485-bidirectional-converter/
- https://www.digikey.fi/en/products/detail/olimex-ltd/USB-RS485/21661988
- https://www.amazon.com/DSD-TECH-SH-U10-Converter-Compatible/dp/B078X5H8H7

---

## Wiring

The CASA Genius ventilation unit has a built-in Modbus RTU interface, brought out through an SEC or SEM connection module. The module connects to the "SEC/SEM" connector on the unit's main board using the included 2-metre cable.

Two pins on the SEC/SEM module's terminal block are used for the Modbus connection: pin 1 is Modbus A and pin 2 is Modbus B. These connect to an RS485-USB converter (e.g. a Waveshare USB to RS485 (B)) so that the converter's A+ terminal connects to Modbus A, and B- connects to Modbus B. The A↔A, B↔B letter matching is a widely followed convention in RS485, so this is a safe starting point — if the connection doesn't come up, the A and B wires can be swapped with no risk of damage.

The RS485-USB converter plugs into the USB port of the device running Home Assistant, where it typically shows up as `/dev/ttyUSB0`. This also matches the integration's default serial port setting.

1. Ventilation unit's connection panel
2. Swegon SEC connection module

![screenshot](SEC_cable.png)

![screenshot](SEC_SEM_wiring.png)

*Note: a GND connection is not used in this wiring. If the bus run gets longer or you experience interference, connecting SEC/SEM pin 8 to the converter's GND terminal for a common ground can improve reliability.*

## Installation

1. Extract the package you received (`swegon_genius_jako.tar.gz`). It contains a folder named `swegon_genius`.

2. Copy the whole `swegon_genius` folder into Home Assistant's folder:

   ```
   /config/custom_components/swegon_genius/
   ```

   If the `custom_components` folder doesn't exist yet, create it first.

   If you're extracting the package directly on the server in a terminal:

   ```
   cd /config/custom_components
   tar -xzf /path/to/swegon_genius_jako.tar.gz
   ```

3. Restart Home Assistant:

   ```
   ha core restart
   ```

---

## Removal

1. Remove the integration from Home Assistant:
  - Open "Settings → Devices & services"
  - Select "Swegon CASA Genius"
  - Select **Delete** (from the three-dot menu)

2. Delete the integration's folder:
   ```
   /config/custom_components/swegon_genius/
   ```

3. Restart Home Assistant

The integration, its entities, and all saved settings are removed.
> **Note:** Dashboards, automations, scripts, helpers, and templates that reference the integration's entities **are not removed automatically**.
> If they reference deleted entities, Home Assistant will show them as *unavailable* until the references are removed or updated.

---

## Setup

1. **Settings → Devices & services → Add integration**
2. Search for **"Swegon CASA Genius"**
3. Enter the connection settings. The defaults suit most setups:

   | Setting | Default | Note |
   |--------|--------|------|
   | Serial port | `/dev/ttyUSB0` | adapter's device path |
   | Slave address | `1` | the unit's Modbus address (1–247) |
   | Baud rate | `38400` | |
   | Stop bits | `1` | |
   | Parity | `N` | |

4. Save. If the connection succeeds, entities will appear under the device.

---

## What's in the package — and what's not

**Included:** the integration itself (entities and controls), plus translations
for five languages (fi/en/sv/nb/da).

**Not included:**
- Dashboard / UI cards — build your own, or don't
- Efficiency template (LTO %) — that's a separate `configuration.yaml` definition
- PIN protection for fan speeds — a dashboard-level feature, not part of the integration

So you get the entities only. Making them visible on a dashboard is your own work.

---

## Entity names and languages

Entity names translate according to the **system language**
(Settings → Home info → Language), NOT the user profile's language. This is
how Home Assistant works. Entity IDs stay the same regardless of language.

Note: entity IDs are generated from your device's name, so they'll differ from
other users'. A finished dashboard can't be copied directly from someone else.

---

## Troubleshooting

**"Connection failed — check the cable, slave address, and serial port"**

- Check the adapter? In a terminal: `ls -l /dev/ttyUSB*`
  If nothing shows up, the adapter isn't connected or the driver wasn't recognized.
- Is the serial port correct? On some systems it's `/dev/ttyUSB1` or `/dev/ttyACM0`.
- Is the slave address correct? Check the Modbus settings on the unit's control panel.
- Is the baud rate the same as the unit's? Default is 38400, but it could be 9600 or 19200.
- Is the bus cable's A/B the right way round? If unsure, try swapping A↔B.

**Entities stay "unavailable"**

- Check that the adapter and cable stay connected.
- Check the logs: Settings → System → Logs, search for "swegon".

---

## Feedback

This is a test version. Let me know what works, what doesn't, and which unit/firmware
you tested with — it helps with finalizing it.
