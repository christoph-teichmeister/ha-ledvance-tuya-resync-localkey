# ha-ledvance-tuya-resync-localkey

pyscript for homeassistant to resync local keys from private tuya API.

This also works for Sylvania devices by changing/uncommenting the keys in `pyscript_modules/tuya/const.py`.

This repository includes

- A script `print_local_keys.py` to print out local keys (and, if the device is reachable on your local network, its
  local IP) for your Ledvance devices (They must be already registered in the Ledvance app), which can be used in the
  [LocalTuya integration](https://github.com/rospogrigio/localtuya) for [Home Assistant](https://www.home-assistant.io/)
- Setup via [Pyscript Integration](https://hacs-pyscript.readthedocs.io/en/latest/) to automatically resync local keys

## To just print out your local keys...

First, install [uv](https://docs.astral.sh/uv/getting-started/installation/) - version 3.10 is confirmed as working.

Then install the dependencies and run the script:

```
uv sync
uv run print_local_keys.py
```

The script reads your Ledvance account credentials from `~/.my-passwords.json`, a JSON list that needs an entry
`{"for": "ledvance", "username": "<email>", "password": "<password>"}`. Never put credentials in the source.

The script also scans your local network (via UDP broadcast) to find each device's local IP address. This only works if
the device is currently online and reachable on the same network segment as the machine running the script - if a device
is offline or on a different network/VLAN, its IP will be reported as not found.

## How to resync local keys automatically (via service)

If you have many devices and reset them sometimes by accident, like me, you can create a service for resyncing the local
keys. (New local keys are generated if you reset/re-register your devices).

### Prerequisites

- [Pyscript Integration](https://hacs-pyscript.readthedocs.io/en/latest/)
- Set `allow_all_imports` and `hass_is_global` to true.
  (Described [here](https://hacs-pyscript.readthedocs.io/en/latest/configuration.html))
- Ledvance account with devices configured

### Setup

- Replace placeholders in `pyscript\sync_tuya_keys.py` with your Ledvance account credentials.
- Copy `pyscript_modules` and `pyscript` to your Home Assistant config directory.
- In your Home Assistant dashboard should now be under `Developer tools` --> `Services` a service called
  `Pyscript Python scripting: synctuyakeys` that you can call. (You may have to restart before)
- (If you want Log output, you need
  to [change the log level to INFO](https://hacs-pyscript.readthedocs.io/en/latest/reference.html#logging) or
  use [jupyter](https://jupyter.org/install))

## LocalTuya setup for light bulbs

When adding a light bulb device in the LocalTuya integration, make sure to select the entity type `light` - **not**
`switch` - before configuring the entity. Otherwise, options like color/color temperature control won't be available.

![LocalTuya light entity configuration](docs/localtuya-light-entity-config.png)

Reference: [How I made tuya-local work with full color controls](https://community.home-assistant.io/t/how-i-made-tuya-local-work-with-full-color-controls/478030/26)

## Credits

Credits for the python Tuya API client go to: https://github.com/rgsilva/homeassistant-positivo
I also extracted the keys/secrets by following his
guide: https://blog.rgsilva.com/reverse-engineering-positivos-smart-home-app/
