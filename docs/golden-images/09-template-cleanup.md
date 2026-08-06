# 09 — SRE Sterilization & Template Freeze Ritual

To prevent cloned VMs from inheriting stale network state, duplicated SSH host keys, identical machine IDs, or leftover logs, a rigorous **Sterilization Ritual** must be executed before converting any VM into a Proxmox template.

---

## 🧹 The Complete Sterilization Sequence

Execute these commands as `abbenden-srv` (via `sudo`) on the instance right before shutdown:

```bash
# ==============================================================================
# STEP 1: CLEAN PACKAGE MANAGER CACHE
# ==============================================================================
sudo apt clean
sudo apt autoremove -y

# ==============================================================================
# STEP 2: CLEAN DOCKER STATE (TEMPLATE 9001 ONLY)
# ==============================================================================
if command -v docker &> /dev/null; then
    sudo docker rm -f $(sudo docker ps -a -q) 2>/dev/null || true
    sudo docker rmi -f hello-world 2>/dev/null || true
    sudo docker system prune -a -f --volumes
fi

# ==============================================================================
# STEP 3: TRUNCATE SYSTEM LOG FILES
# ==============================================================================
# Truncate all log files to zero length while preserving ownership and permissions
sudo find /var/log -type f -exec truncate -s 0 {} \;
sudo rm -f /var/log/*.gz /var/log/*.[0-9] /var/log/*-????????

# ==============================================================================
# STEP 4: RESET MACHINE ID (CRITICAL FOR NETWORK & DHCP)
# ==============================================================================
# Systemd machine-id must be empty so systemd-genid creates a fresh unique ID on first boot
sudo truncate -s 0 /etc/machine-id
sudo rm -f /var/lib/dbus/machine-id
sudo ln -s /etc/machine-id /var/lib/dbus/machine-id

# ==============================================================================
# STEP 5: REMOVE TEMPORARY FILES & BASH HISTORY
# ==============================================================================
sudo rm -rf /tmp/* /var/tmp/*
history -c && history -w

# ==============================================================================
# STEP 6: POWER OFF INSTANCE
# ==============================================================================
sudo poweroff
```

---

## 🚫 Why Cloud-Init State Reset is NOT Needed

> 💡 **Architectural Note**: HoRus-Start explicitly avoids `cloud-init` in Golden Templates. `cloud-init` introduces boot delays (2–3 minutes searching for cloud datasources), requires fake ISO mounts in Proxmox, and frequently caches stale instance IDs. 
>
> Instead, network configuration, hostname setting, and SSH key management are performed directly by **Ansible** during post-clone execution or via `qemu-guest-agent`.

---

## ❄️ Proxmox Template Conversion Steps

Once the VM shuts down cleanly:

1. Open Proxmox VE Web UI.
2. Verify VM status is **Stopped** (Icon turns grey).
3. Right-click the VM (e.g. `9000` or `9001`) ➔ Click **Convert to Template**.
4. Confirm conversion. The VM icon changes to a template sheet icon.
