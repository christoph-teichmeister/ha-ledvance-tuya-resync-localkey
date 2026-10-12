#!/usr/bin/env python3

import json
from pathlib import Path

import tinytuya

from pyscript_modules.tuya.api import TuyaAPI
from pyscript_modules.tuya.exceptions import InvalidAuthentication

CREDENTIALS_FILE = Path.home() / ".my-passwords.json"


def load_credentials():
    """Ledvance app login from the entry `{"for": "ledvance", "email": ..., "password": ...}`."""
    entries = json.loads(CREDENTIALS_FILE.read_text())
    entry = next((e for e in entries if e.get("for") == "ledvance"), None)
    if not entry:
        exit(f'No entry with "for": "ledvance" in {CREDENTIALS_FILE}.')
    return {"email": entry["email"], "password": entry["password"]}


def main():
    api = TuyaAPI(**load_credentials())
    try:
        api.login()
    except InvalidAuthentication:
        print("Invalid authentication.")
        exit(1)

    print('scanning local network for devices...')
    scanned_devices = tinytuya.deviceScan(verbose=False)
    local_ips_by_dev_id = {info["gwId"]: ip for ip, info in scanned_devices.items()}

    print('---------------------------')

    for group in api.groups():
        for dev in api.devices(group['groupId']):
            local_ip = local_ips_by_dev_id.get(dev.id, "not found on local network")
            print(f'device name:\t{dev.name}')
            print(f'device id:\t\t{dev.id}')
            print(f'local key:\t\t{dev.localKey}')
            print(f'local ip:\t\t{local_ip}')
            print('---------------------------')

if __name__ == "__main__":
    main()
