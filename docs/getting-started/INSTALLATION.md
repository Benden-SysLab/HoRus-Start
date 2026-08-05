# HoRus-Start Installation Guide

This guide details the steps to set up the control node environment for running **HoRus-Start v2**.

---

## Prerequisites

The control node (machine executing Ansible playbooks and Python scripts) requires:

- **Operating System**: Linux (Debian 12/13, Ubuntu 22.04/24.04, or macOS/RHEL with Python 3.10+)
- **Python**: `python3` (>= 3.10) with `pip`
- **Ansible**: `ansible-core` (>= 2.15)
- **OpenSSH Client**: `ssh-keygen`, `ssh`

---

## Step 1: Clone Repository

```bash
git clone https://github.com/your-org/HoRus-Start.git
cd HoRus-Start
```

---

## Step 2: Install Python & Ansible Dependencies

Install required Python modules for schema validation and playbook execution:

```bash
pip3 install -r requirements.txt || pip3 install pyyaml jsonschema ansible-core
```

Verify Python & Ansible versions:

```bash
python3 --version
ansible --version
```

---

## Step 3: Configure Inventory & Node Credentials

1. **Inventory (`inventory/hosts.yml`)**: Update target IP addresses and hostnames for your Proxmox VE nodes.
2. **Credentials (`credentials/proxmox_credentials.yml`)**: Define root credentials for initial SSH key deployment during Stage 0 & 1.

```bash
cp config/examples/cluster.example.yml config/cluster.yml
cp config/examples/network.example.yml config/network.yml
cp config/examples/storage.example.yml config/storage.yml
```

---

## Step 4: Run Readiness Preflight Gate (Stage 0)

```bash
python3 scripts/stage0_preflight.py
```

If Stage 0 outputs `[PASS]`, your installation and credentials are validated and ready for full pipeline execution.
