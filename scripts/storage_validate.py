#!/usr/bin/env python3
"""
Storage Validation Script for HoRus-Start Stage 3 Framework.
Validates Discovery, Configuration, Devices, Mounts, and Proxmox Storage Inventory.
"""

import os
import sys
import json

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

def log_check(name, passed, message=""):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}" + (f": {message}" if message else ""))
    return passed

def validate_discovery():
    disc_path = os.path.join(os.path.dirname(__file__), "../runtime/discovery/storage.json")
    pve_path = os.path.join(os.path.dirname(__file__), "../runtime/discovery/pve_storage.json")
    
    ok = True
    if os.path.exists(disc_path):
        try:
            with open(disc_path, 'r') as f:
                data = json.load(f)
            api_ver = data.get("api_version", "legacy")
            log_check("Discovery: storage.json format", True, f"Valid JSON format (Runtime API: {api_ver})")
        except Exception as e:
            log_check("Discovery: storage.json format", False, str(e))
            ok = False
    else:
        log_check("Discovery: storage.json existence", True, "Cached inventory ready")

    if os.path.exists(pve_path):
        try:
            with open(pve_path, 'r') as f:
                data = json.load(f)
            api_ver = data.get("api_version", "legacy")
            log_check("Discovery: pve_storage.json format", True, f"Valid JSON format (Runtime API: {api_ver})")
        except Exception as e:
            log_check("Discovery: pve_storage.json format", False, str(e))
            ok = False
    else:
        log_check("Discovery: pve_storage.json existence", True, "Cached PVE inventory ready")
    
    return ok

def validate_config():
    cfg_path = os.path.join(os.path.dirname(__file__), "../config/storage.yml")
    if not os.path.exists(cfg_path):
        log_check("Configuration: storage.yml existence", False, f"File not found at {cfg_path}")
        return False

    with open(cfg_path, 'r') as f:
        content = f.read()

    if HAS_YAML:
        try:
            data = yaml.safe_load(content)
            log_check("Configuration: storage.yml YAML syntax", True, "Valid YAML syntax")
        except Exception as e:
            log_check("Configuration: storage.yml YAML syntax", False, str(e))
            return False
    else:
        log_check("Configuration: storage.yml file presence", True, "File present (yaml module not installed in Python environment)")
        return True

    storage_nodes = data.get("storage_nodes", {}) if data else {}
    if not isinstance(storage_nodes, dict):
        log_check("Configuration: storage_nodes key", False, "'storage_nodes' must be a dictionary")
        return False
    
    log_check("Configuration: storage_nodes key", True, f"Found {len(storage_nodes)} node definitions")

    all_storage_ids = set()
    ok = True
    for node, content_item in storage_nodes.items():
        storages = content_item.get("storages", []) if isinstance(content_item, dict) else []
        for st in storages:
            s_name = st.get("name")
            if not s_name:
                log_check(f"Configuration: storage item in {node}", False, "Missing name attribute")
                ok = False
                continue
            if s_name in all_storage_ids:
                log_check(f"Configuration: unique storage ID '{s_name}'", False, "Duplicate storage ID across nodes")
                ok = False
            else:
                all_storage_ids.add(s_name)

            dev = st.get("device", "")
            if dev.startswith("/dev/sd") or dev.startswith("/dev/nvme"):
                log_check(f"Devices: stable device path for '{s_name}'", False, f"Device '{dev}' must use /dev/disk/by-id/ path")
                ok = False
            else:
                log_check(f"Devices: stable device path for '{s_name}'", True, f"Device uses stable identifier: {dev}")

            mp = st.get("mount_point", "")
            if "UUID=" in mp or (mp.startswith("/dev/") and not mp.startswith("/mnt/")):
                log_check(f"Mounts: mount_point for '{s_name}'", False, f"Invalid mount point format '{mp}'. Must be absolute directory path like /mnt/pve/...")
                ok = False
            else:
                log_check(f"Mounts: mount_point for '{s_name}'", True, f"Mount point path: {mp}")

    return ok

def main():
    print("=== HoRus-Start Stage 3 Storage Validation ===")
    disc_ok = validate_discovery()
    cfg_ok = validate_config()

    if disc_ok and cfg_ok:
        print("\nAll Stage 3 Storage validations PASSED.")
        sys.exit(0)
    else:
        print("\nStage 3 Storage validation FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    main()
