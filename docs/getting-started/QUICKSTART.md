# Quickstart Guide — HoRus-Start v2

Get your Proxmox VE cluster bootstrapped, configured, and stocked with OS assets in 5 simple steps.

---

## Step 1: Execute Preflight Readiness Gate (Stage 0)

Validate target host connectivity, configuration syntax, and credential formats:

```bash
python3 scripts/stage0_preflight.py
```

---

## Step 2: Run SSH Bootstrap (Stage 1)

Generate local ed25519 SSH keys and deploy passwordless SSH access to all target nodes:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/00_bootstrap_connectivity.yml
```

---

## Step 3: Base System Standardization (Stage 2) & Cluster Setup (Stage 3)

Configure APT repositories (no-subscription), install base utilities, sysctl kernel parameters, and create the Proxmox cluster:

```bash
# Stage 2: Base System Prep
ansible-playbook -i inventory/hosts.yml playbooks/01_base_system_prep.yml

# Stage 3: Proxmox Cluster Formation
ansible-playbook -i inventory/hosts.yml playbooks/02_proxmox_cluster.yml
```

---

## Step 4: Storage Provisioning (Stage 4)

Plan and format physical storage drives identified by persistent `/dev/disk/by-id/` IDs:

```bash
# Dry-run planning mode (generates runtime/plans/storage_plan.json)
ansible-playbook -i inventory/hosts.yml playbooks/03_storage_prepare.yml -e "storage_plan_only=true"

# Provision storage volumes & register in PVE
ansible-playbook -i inventory/hosts.yml playbooks/03_storage_prepare.yml
```

---

## Step 5: Asset Preparation & Validation (Stage 5)

Download cloud images, ISO catalog assets, VirtIO drivers, and LXC template caches, publishing them directly into PVE storage:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/04_proxmox_templates.yml
```

---

## Interactive Launcher Option

Alternatively, use the interactive CLI launcher:

```bash
./horus-start
```

---

## Verification & Status Reports

Inspect stage completion status and Runtime API reports at any time:

```bash
python3 scripts/validate_schemas.py
cat runtime/reports/stage5.json
```
