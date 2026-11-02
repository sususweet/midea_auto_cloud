# Midea Auto Cloud

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![Stable](https://img.shields.io/github/v/release/sususweet/midea-meiju-codec)](https://github.com/sususweet/midea-meiju-codec/releases/latest)

English | [简体中文](README_hans.md)

Get devices from MSmartHome/Midea Meiju homes through the network and control them via Midea's cloud API.

- Automatically discover and find devices
- Automatically download device protocol files
- Update device status to visible device attributes

## Version Notes

- All devices can generate a binary sensor named "Status" by default, which lists all accessible device attributes in its properties (some values are not settable)
- The first few items of the Status entity list the device classification information for reference

## Currently Supported Device Types

- T0x13 Electric Light
- T0x15 Water Heater
- T0x17 Laundry Machine
- T0x21 Central Air Conditioning Gateway
- T0x24 Electric Oven
- T0x26 Bath Heater
- T0x3D Water Heater
- T0x44 Smart Thermostat
- T0x5D Ice Maker
- T0x9B Steam oven
- T0x9C Integrated Gas Stove
- T0xA1 Dehumidifier
- T0xAC Air Conditioner
- T0xB0 Microwave Oven
- T0xB2 Electric Steamer
- T0xB3 Disinfection Cabinet
- T0xB6 Range Hood
- T0xB7 Gas Stove
- T0xB8 Smart Robot Vacuum
- T0xBC Air Sensor
- T0xBF Microwave Steam Oven
- T0xC1 Wall hanging furnace
- T0xC2 Intelligent Toilet
- T0xC3 Heat Pump
- T0xCA French Door Refrigerator
- T0xCC Central Air Conditioning (Ducted) Wi-Fi Controller
- T0xCD Air Energy Water Heater
- T0xCE Fresh Air System
- T0xCF Central Air Conditioning Heating
- T0xD9 Twin Tub Washing Machine
- T0xDA Impeller Washing Machine
- T0xDB Cylinder Washing Machine
- T0xDC Clothes Dryer
- T0xE1 Dishwasher
- T0xE2 Electric Water Heater
- T0xE3 Constant Temperature Gas Water Heater
- T0xE6 Wall hanging furnace
- T0xE7 Electric Oven
- T0xEA Rice Cooker
- T0xED Water Softener
- T0xFA Electric Fan
- T0xFB Electric Heater
- T0xFC Air Purifier
- T0xFD Humidifier

Welcome to collaborate on adding support for more devices.

Collaboration method: After adding this plugin, find devices that are not correctly identified, click on `Connectivity` under the `Sensor` category of the corresponding device:

![img.png](./img/img.png)

Expand the `Attributes` card below and submit these fields with the issue. Pay special attention to the `Device type` and `Subtype` fields, as these are the basis for obtaining the corresponding lua files for device control.

Then go to the Home Assistant installation directory, find the device's corresponding T_0000_`Device type`_`Subtype`_***.lua file in the `.storage/midea_auto_cloud/lua/` directory and `zip` file in the `.storage/midea_auto_cloud/plugin/` directory, and wait for adaptation.

![img_1.png](./img/img_1.png)

## Entity Mapping

Mapping files are located under `device_mapping`, with one mapping file for each major category. Currently supported entity types for mapping are:
- sensor
- binary_sensor
- switch
- select
- climate
- fan
- water_heater

The example configuration `22012227` demonstrates how to map device attributes to various Home Assistant entities above.

### External mapping overlay (per device)

When multiple appliances share the same `device_type` / `sn8` / `subtype` but need different entity mappings (e.g. Clivet indoor units), open **Configure → Options → Device mapping overlay**:

1. Select a device (name / type / device_id)
2. **Paste JSON** to create/update a profile, or **use an existing profile**
3. Save; the config entry reloads automatically

Data lives under `.storage/midea_auto_cloud/mappings/` (survives integration upgrades):

```text
.storage/midea_auto_cloud/mappings/
  overrides.json          # device_id -> profile_id
  <profile_id>.json
```

Example profile (`mode: extend` merges onto builtin mapping; `replace` replaces it):

```json
{
  "profile": "clivet_cassette",
  "device_type": "T0xCC",
  "mode": "extend",
  "mapping": {
    "entities": {
      "climate": {
        "thermostat": {
          "fan_modes": { "1": {"wind_speed_level": "1"} }
        }
      }
    }
  }
}
```

Platform keys under `entities` are strings (`climate` / `switch`, …). Set a key to `null` in an extend overlay to remove that builtin entry. Stable fragments are welcome as PRs back into `device_mapping/`.

## Donation

If you find the project interesting or helpful, you are welcome to make a donation to support it. Donations will be used for the daily maintenance of the plugin, making it easier to provide better services for everyone!

[!["Buy Me A Coffee"](https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png)](https://www.buymeacoffee.com/sususweet)

## Acknowledgments

Thanks to the [midea-meiju-codec](https://github.com/MattedBroadSky/midea-meiju-codec) project for providing prior knowledge.
