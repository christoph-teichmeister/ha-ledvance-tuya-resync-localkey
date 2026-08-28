#!/usr/bin/env python3

from pyscript_modules.tuya.api import TuyaAPI
from pyscript_modules.tuya.exceptions import InvalidAuthentication

def main():
    api = TuyaAPI(email="you@example.com", password="REDACTED")
    try:
        api.login()
    except InvalidAuthentication:
        print("Invalid authentication.")
        exit(1)

    print('---------------------------')

    for group in api.groups():
        for dev in api.devices(group['groupId']):
            print(f'device name:\t{dev.name}')
            print(f'device id:\t\t{dev.id}')
            print(f'local key:\t\t{dev.localKey}')
            print('---------------------------')

if __name__ == "__main__":
    main()
