# HoRus-Start — Proxmox VE IaC Infrastructure Platform

🌐 **Languages**: **English** | [Русский](./README.ru.md) | [Українська](./README.uk.md) | [日本語](./README.ja.md) | [Deutsch](./README.de.md) | [Français](./README.fr.md)

---

## 🏛️ Executive Summary & Vision

**HoRus-Start** is an enterprise-grade Infrastructure-as-Code (IaC) automation framework designed for bootstrapping, provisioning, and managing bare-metal Proxmox VE hypervisor clusters. Built upon declarative principles, modular Ansible roles, and versioned JSON Runtime APIs, HoRus-Start provides end-to-end lifecycle management from bare-metal network connectivity to distributed storage and cloud image deployment.

> 🔒 **Architecture Freeze Notice**: Stages 0–4 are fully operational, idempotent, and stabilized under **Architecture Stabilization Milestone (Pre-Stage 5)**.

---

## 🚀 Execution Pipeline & Stage Architecture

HoRus-Start enforces a deterministic 5-step pipeline across all infrastructure stages:

```
[ Declarative Config ] ──► 1. Discovery ──► 2. Normalization ──► 3. Planning ──► 4. Provisioning ──► 5. Verification & Reports
```

### Stage Overview

| Stage | Name | Description | Status |
| :--- | :--- | :--- | :--- |
| **Stage 0** | **Infrastructure Readiness Gate** | Non-destructive preflight validation, credentials bootstrapping, hardware auto-discovery, artifact checksum verification, and `stage0.json` gate generation. | **STABLE** |
| **Stage 1** | **Bootstrap Connectivity** | Probes target nodes, generates ed25519 SSH keys, deploys public keys, and validates passwordless root SSH access. | **STABLE** |
| **Stage 2** | **Base System Prep** | Configures APT repositories (pve-no-subscription), performs kernel updates, installs core toolsets, and tunes sysctl settings. | **STABLE** |
| **Stage 3** | **Proxmox Cluster** | Initializes pvecm quorum cluster across nodes (`horus-pmx-node01` through `node04`), configures corosync network links. | **STABLE** |
| **Stage 4** | **Storage Prepare** | Safely discovers physical block devices (`/dev/disk/by-id/`), validates OS disk safety, plans mounts, formats ext4/ZFS, and registers PVE directory volumes. | **STABLE** |
| **Stage 5** | **Golden Image Factory** | Downloads cloud OS images (Ubuntu, Debian, Alpine), creates Proxmox Cloud-Init VM templates. | *Next Stage* |
| **Stage 6** | **Platform Bootstrap** | Management infrastructure setup: terraform-srv, dedicated SSH keys, sudoers, API tokens, and service accounts. | *Planned* |
| **Stage 7** | **Security** | System security hardening: sysctl kernel parameters, sshd configuration, fail2ban, motd banners, and system limits. | *Planned* |
| **Stage 8** | **Verification** | Full platform self-test auditing Cluster, Storage, Images, Templates, Users, SSH, Security, and Reports. | *Planned* |

---

## 💾 Stage 4 Storage Framework Architecture

Stage 4 provides a production-grade storage reconciliation engine:

1. **Discovery**: Scans node block devices via `lsblk -J` and maps persistent `/dev/disk/by-id/` symlinks without altering disk state.
2. **OS Safety Guard**: Formally asserts that no target storage overlaps with system OS parent drives (`/`, `/boot`, `/boot/efi`, `/etc/pve`).
3. **Planner**: Computes precise diffs (`needs_format`, `needs_mkdir`, `needs_mount`, `needs_pvesm_add`) saved to `runtime/plans/storage_plan.json`.
4. **Provisioning**: Creates systemd mount units, formats filesystems with strict safety checks, updates `/etc/fstab`, and registers storages in Proxmox.
5. **Verification**: Conducts post-provisioning audits, verifies active mounts via `findmnt`, detects drift, and exports `runtime/reports/stage4.json`.

---

## 📡 Runtime API v1 & Domain Model

Cross-stage communication in HoRus-Start is governed by **Runtime API v1**, eliminating hidden coupling and fragile task variables.

- **Config (`config/`)**: Single source of truth for desired state.
- **Runtime (`runtime/`)**: Single source of truth for actual/planned state.
  - `runtime/discovery/` — Discovered hardware inventory.
  - `runtime/facts/` — Normalized infrastructure facts.
  - `runtime/plans/` — Machine-readable execution plans.
  - `runtime/reports/` — Drift detection and stage completion reports.
  - `runtime/cache/`, `runtime/locks/`, `runtime/state/` — Private stage state.

All public runtime JSON objects adhere to schemas in `schemas/runtime/` and contain top-level contract headers (`api_version: "v1"`, `schema_version: "1.0"`).

---

## 📁 Repository Directory Layout

```
HoRus-Start/
├── config/                  # Declarative cluster & storage configurations (SOT)
│   ├── storage.yml
│   └── storage_templates/
├── credentials/             # Local SSH keys and vault credentials (GIT-IGNORED)
├── docs/                    # Architecture documentation & frozen contracts
│   └── architecture/
│       ├── ARCHITECTURE_FREEZE.md
│       ├── DOMAIN_MODEL.md
│       ├── PLANNER_SPEC.md
│       └── RUNTIME_API_V1.md
├── inventory/               # Ansible inventory definitions (hosts.yml)
├── playbooks/               # Main execution playbooks (00_*.yml through 04_*.yml)
├── plugins/                 # Custom Ansible filter & action plugins
├── roles/                   # Modular domain roles (storage_prepare, etc.)
├── runtime/                 # Versioned Runtime API v1 objects (GIT-IGNORED)
│   ├── discovery/
│   ├── facts/
│   ├── plans/
│   └── reports/
├── schemas/                 # JSON Schemas for config and runtime validation
├── scripts/                 # Validation and schema verification utilities
│   ├── storage_validate.py
│   └── validate_schemas.py
├── horus-start              # Interactive CLI launcher
└── README.md                # Primary documentation
```

---

## 🛠️ Usage & Operations

### 1. Execute Interactive Launcher
```bash
./horus-start
```

### 2. Run Preflight & Stage Playbooks
```bash
# Stage 0: Infrastructure Readiness Gate (Preflight Control Plane)
python3 scripts/stage0_preflight.py

# Stage 1: Connectivity Bootstrap
ansible-playbook -i inventory/hosts.yml playbooks/00_bootstrap_connectivity.yml

# Stage 2: Base System Prep
ansible-playbook -i inventory/hosts.yml playbooks/01_base_system_prep.yml

# Stage 3: Proxmox Cluster Setup
ansible-playbook -i inventory/hosts.yml playbooks/02_proxmox_cluster.yml

# Stage 4: Storage Preparation (Dry-run / Plan-only mode)
ansible-playbook -i inventory/hosts.yml playbooks/03_storage_prepare.yml -e "storage_plan_only=true"

# Stage 4: Storage Preparation (Provisioning execution)
ansible-playbook -i inventory/hosts.yml playbooks/03_storage_prepare.yml
```

### 3. Run Validation Scripts
```bash
# Validate Storage Configuration & Discovery
python3 scripts/storage_validate.py

# Validate Runtime API v1 JSON Schemas
python3 scripts/validate_schemas.py
```

---

## 🔒 Security & Privacy

All sensitive files, including private SSH keys (`credentials/ssh/*`), vault passwords (`.vault_pass`), `.env` files, and temporary execution logs are strictly ignored in `.gitignore`. Never commit credentials to version control.
