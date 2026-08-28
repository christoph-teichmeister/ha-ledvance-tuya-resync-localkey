#!/usr/bin/env python3

import tinytuya

from pyscript_modules.tuya.api import TuyaAPI
from pyscript_modules.tuya.exceptions import InvalidAuthentication

def main():
    api = TuyaAPI(email="you@example.com", password="REDACTED")
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
