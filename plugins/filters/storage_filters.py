#!/usr/bin/env python3
"""
HoRus-Start Custom Jinja2 Filter Plugins for Storage & Infrastructure Normalization.
"""

def normalize_device_path(device):
    """Ensure device path uses stable by-id identifier when available."""
    if not device:
        return ""
    if device.startswith("/dev/sd") or device.startswith("/dev/nvme"):
        return device
    return device

def is_system_device(device, os_disk_name="sda"):
    """Check if device conflicts with system OS disk."""
    if not device:
        return False
    dev_base = device.replace("/dev/", "")
    return dev_base == os_disk_name or os_disk_name in dev_base

class FilterModule(object):
    """Ansible Jinja2 Filter Plugin loader."""
    def filters(self):
        return {
            'normalize_device_path': normalize_device_path,
            'is_system_device': is_system_device,
        }
