"""Pyscript app: update LocalTuya local keys that changed in the Ledvance cloud (reset/re-paired lamps).

Deploy: this file to /config/pyscript/apps/, pyscript_modules/tuya to /config/pyscript_modules/ledvance_tuya,
pyscript/requirements.txt to /config/pyscript/. Config (configuration.yaml):

    pyscript:
      allow_all_imports: true
      hass_is_global: true
      apps:
        ledvance_resync:
          email: !secret ledvance_email
          password: !secret ledvance_password
"""
import copy
import sys

if "/config/pyscript_modules" not in sys.path:
    sys.path.append("/config/pyscript_modules")

from ledvance_tuya.api import TuyaAPI


@pyscript_executor
def fetch_cloud_keys(email, password):
    api = TuyaAPI(email=email, password=password)
    api.login()
    return {d.id: d.localKey for g in api.groups() for d in api.devices(g["groupId"])}


@service(supports_response="optional")
def ledvance_resync_keys():
    """Update LocalTuya local keys that changed in the Ledvance cloud and reload the entry."""
    keys = fetch_cloud_keys(pyscript.app_config["email"], pyscript.app_config["password"])
    updated = []
    for entry in hass.config_entries.async_entries("localtuya"):
        data = copy.deepcopy(dict(entry.data))
        before = len(updated)
        for dev_id, dev in data["devices"].items():
            if keys.get(dev_id) and keys[dev_id] != dev["local_key"]:
                dev["local_key"] = keys[dev_id]
                updated.append(dev["friendly_name"])
        if len(updated) > before:
            hass.config_entries.async_update_entry(entry, data=data)
            hass.config_entries.async_schedule_reload(entry.entry_id)
    log.info(f"Ledvance key resync: updated {updated or 'nothing'}")
    return {"updated": updated}
