#!/usr/bin/env python3
"""Push changed Ledvance local keys into Home Assistant's LocalTuya integration.

Compares every LocalTuya device's key with the Ledvance cloud and updates only the changed ones through the
LocalTuya options flow ("Edit a device"); entity IDs survive. Credentials come from ~/.my-passwords.json:
`{"for": "ledvance", ...}` (see print_local_keys.py) and `{"for": "homeassistant", "password": "<long-lived token>"}`.

    uv run resync_ha_local_keys.py [--dry-run] [--url https://homeassistant.local:8123]
"""
import argparse
import json
import ssl
import urllib.request

from print_local_keys import CREDENTIALS_FILE, load_credentials
from pyscript_modules.tuya.api import TuyaAPI


def ha_client(url):
    token = next(e["password"] for e in json.loads(CREDENTIALS_FILE.read_text()) if e.get("for") == "homeassistant")
    # ponytail: no cert check, HA serves a self-signed cert on the LAN
    ctx = ssl._create_unverified_context()

    def call(method, path, body=None):
        req = urllib.request.Request(f"{url}/api/{path}", method=method,
                                     data=json.dumps(body).encode() if body is not None else None,
                                     headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
        with urllib.request.urlopen(req, context=ctx) as resp:
            return json.loads(resp.read() or "null")

    return call


def defaults(form):
    """Current values of a flow form: defaults, overridden by suggested values."""
    values = {f["name"]: f["default"] for f in form["data_schema"] if "default" in f}
    values |= {f["name"]: f["description"]["suggested_value"] for f in form["data_schema"]
               if (f.get("description") or {}).get("suggested_value") is not None}
    return values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="only report which keys changed")
    parser.add_argument("--url", default="https://homeassistant.local:8123")
    args = parser.parse_args()

    api = TuyaAPI(**load_credentials())
    api.login()
    cloud = {d.id: (d.name, d.localKey) for g in api.groups() for d in api.devices(g["groupId"])}

    call = ha_client(args.url)
    entries = [e for e in call("GET", "config/config_entries/entry") if e["domain"] == "localtuya"]
    for entry in entries:
        flow = call("POST", "config/config_entries/options/flow", {"handler": entry["entry_id"]})
        fid = flow["flow_id"]
        devices = next(f["options"] for f in call("POST", f"config/config_entries/options/flow/{fid}",
                                                  {"action": "edit_device"})["data_schema"])
        call("DELETE", f"config/config_entries/options/flow/{fid}")

        for dev_id, _label in devices:
            name, cloud_key = cloud.get(dev_id, (dev_id, None))
            fid = call("POST", "config/config_entries/options/flow", {"handler": entry["entry_id"]})["flow_id"]
            path = f"config/config_entries/options/flow/{fid}"
            call("POST", path, {"action": "edit_device"})
            form = call("POST", path, {"selected_device": dev_id})
            current = defaults(form)
            if not cloud_key or cloud_key == current["local_key"] or args.dry_run:
                call("DELETE", path)
                state = "not in Ledvance cloud" if not cloud_key else (
                    "up to date" if cloud_key == current["local_key"] else "KEY CHANGED")
                print(f"{name}: {state}")
                continue
            form = call("POST", path, current | {"local_key": cloud_key, "add_entities": False})
            while form.get("step_id") == "configure_entity":
                form = call("POST", path, defaults(form))
            assert form["type"] == "create_entry", form
            print(f"{name}: key updated")


if __name__ == "__main__":
    main()
