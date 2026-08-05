# Operational Troubleshooting Guide — HoRus-Start v2

This document details common operational issues, diagnostics, and step-by-step resolution procedures.

---

## 1. Stage 0 & 1: SSH Connectivity & Password Failures

### Symptom
`stage0_preflight.py` reports `FAILED` or Stage 1 SSH key deployment fails with `Permission denied (publickey,password)`.

### Root Cause
- Incorrect root password in `credentials/proxmox_credentials.yml`.
- Target node root password login disabled in `/etc/ssh/sshd_config` (`PermitRootLogin`).

### Resolution
1. Verify node password by manually logging in via SSH:
   ```bash
   ssh root@<TARGET_IP>
   ```
2. If root password login is disabled, enable temporary password login on target node:
   ```bash
   sed -i 's/^PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
   systemctl restart ssh
   ```
3. Re-run Stage 0 preflight and Stage 1 playbook.

---

## 2. Stage 3: Proxmox Cluster Quorum Issues

### Symptom
`pvecm status` shows `Quorum: Activity blocked` or cluster nodes fail to join.

### Root Cause
- Firewall blocking UDP ports 5405–5412 (Corosync).
- Hostname resolution mismatch across cluster nodes.

### Resolution
1. Verify `/etc/hosts` on all nodes contains consistent mappings for all cluster members.
2. Check Corosync service logs:
   ```bash
   journalctl -u corosync -n 50 --no-pager
   ```
3. Ensure firewalls allow Corosync traffic between node IPs.

---

## 3. Stage 4: Storage Safety Guard Triggered

### Symptom
Stage 4 provisioning aborts with `SAFETY GUARD TRIGGERED: Target device is root disk`.

### Root Cause
The configured `device` path in `config/storage.yml` resolves to the drive hosting `/`, `/boot`, or `/etc/pve`.

### Resolution
1. Run disk discovery to inspect disk serial numbers:
   ```bash
   lsblk -o NAME,FSTYPE,MOUNTPOINT,SIZE,MODEL /dev/disk/by-id/*
   ```
2. Ensure target data storage devices do not overlap with OS system partitions. Update `config/storage.yml` with the correct disk ID.

---

## 4. Stage 5: Asset Download Failures

### Symptom
Stage 5 fails downloading cloud images or ISO assets with HTTP timeouts or `qemu-img info` validation failures.

### Root Cause
- Outbound internet connection issues or broken upstream download URL.
- Partial/corrupted download file in `target_storage_dir`.

### Resolution
1. Verify outbound internet connectivity on builder node:
   ```bash
   curl -I https://cloud.debian.org/images/cloud/trixie/latest/debian-13-genericcloud-amd64.qcow2
   ```
2. Delete partial download files from target storage directory and re-run Stage 5.
