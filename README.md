# HoRus-Start — Proxmox VE IaC Infrastructure Platform (v2.0-RC1)

🌐 **Languages**: **English** | [Русский](./README.ru.md) | [Українська](./README.uk.md) | [日本語](./README.ja.md) | [Deutsch](./README.de.md) | [Français](./README.fr.md)

---

## 🏛️ Executive Summary & Architectural Scope

**HoRus-Start v2** is an enterprise-grade Infrastructure-as-Code (IaC) automation framework designed for bootstrapping bare-metal Proxmox VE hypervisor clusters. Built upon declarative principles, modular Ansible roles, and versioned JSON Runtime APIs (v1), HoRus-Start provides deterministic automation from bare-metal network readiness to distributed storage reconciliation and OS asset publication.

> 🔒 **Architecture Freeze Notice (v2.0-RC1)**: The HoRus-Start pipeline is frozen and permanently limited to **Stages 0 through 5**. The pipeline finishes upon completing Stage 5 (Asset Preparation & Validation). Manual Golden Template creation, Terraform provisioning, and application deployments operate outside HoRus-Start.

---

## 🚀 Execution Pipeline & Stage Architecture

HoRus-Start enforces a deterministic 5-step lifecycle across all active infrastructure stages:

```
[ Declarative Config ] ──► 1. Discovery ──► 2. Normalization ──► 3. Planning ──► 4. Provisioning ──► 5. Verification & Reports
```

### Stage Overview

| Stage | Name | Description | Status |
| :--- | :--- | :--- | :--- |
| **Stage 0** | **Infrastructure Readiness Gate** | Preflight validation, credential formatting, host discovery, checksum verification, and `stage0.json` gate generation. | **STABLE** |
| **Stage 1** | **Bootstrap Connectivity** | Probes target nodes, generates local ed25519 SSH keys, deploys public keys, and validates passwordless root SSH access. | **STABLE** |
| **Stage 2** | **Base System Prep** | Configures APT repositories (Debian 13 Trixie & PVE no-subscription), updates kernel, installs base toolsets, tunes sysctl parameters. | **STABLE** |
| **Stage 3** | **Proxmox Cluster** | Initializes `pvecm` quorum cluster across nodes, configures corosync inter-node network links. | **STABLE** |
| **Stage 4** | **Storage Prepare** | Discovers physical block devices (`/dev/disk/by-id/`), asserts OS disk safety, plans mounts, formats ext4/ZFS, and registers PVE directory volumes. | **STABLE** |
| **Stage 5** | **Asset Preparation & Validation** | Downloads cloud images, ISO catalog, VirtIO drivers, and LXC template caches; publishes assets to PVE storage; validates checksums & `qemu-img` integrity. | **STABLE** |

> 🛑 **Pipeline Termination**: The automation pipeline ends after Stage 5.

---

## 💾 Storage Framework Architecture (Stage 4)

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
├── .github/                 # CI/CD Workflows (secret scan, yaml validation, ansible lint)
├── config/                  # Declarative cluster & storage configurations
│   ├── examples/            # Example cluster, network, and storage configurations
│   ├── storage.yml
│   └── image_catalog.yml
├── credentials/             # Local SSH keys and vault credentials (GIT-IGNORED)
├── docs/                    # Architecture, Getting Started, Operations & Security docs
│   ├── architecture/        # Domain model, planner spec, runtime API specifications
│   ├── getting-started/     # Installation, Quickstart, Requirements
│   ├── operations/          # Troubleshooting, Recovery, Backup & Restore
│   └── security/            # Security Model, Secrets Management, Threat Model
├── inventory/               # Ansible inventory definitions (hosts.yml)
├── playbooks/               # Main execution playbooks (00_*.yml through 04_*.yml)
├── plugins/                 # Custom Ansible filter & action plugins
├── roles/                   # Modular domain roles (storage_prepare, proxmox_templates, etc.)
├── runtime/                 # Versioned Runtime API v1 objects (GIT-IGNORED)
├── schemas/                 # JSON Schemas for config and runtime validation
├── scripts/                 # Validation and preflight CLI tools
│   ├── stage0_preflight.py
│   ├── storage_validate.py
│   └── validate_schemas.py
├── horus-start              # Interactive CLI launcher
├── SECURITY.md              # Security policy & vulnerability reporting
├── CONTRIBUTING.md          # Contribution guidelines
├── CODE_OF_CONDUCT.md       # Community standards
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

# Stage 1: Connectivity Bootstrap & SSH Mesh
ansible-playbook -i inventory/hosts.yml playbooks/00_bootstrap_connectivity.yml

# Stage 2: Base System Prep & Debian 13 Standardization
ansible-playbook -i inventory/hosts.yml playbooks/01_base_system_prep.yml

# Stage 3: Proxmox Cluster Setup
ansible-playbook -i inventory/hosts.yml playbooks/02_proxmox_cluster.yml

# Stage 4: Storage Preparation (Dry-run / Plan-only mode)
ansible-playbook -i inventory/hosts.yml playbooks/03_storage_prepare.yml -e "storage_plan_only=true"

# Stage 4: Storage Preparation (Provisioning execution)
ansible-playbook -i inventory/hosts.yml playbooks/03_storage_prepare.yml

# Stage 5: Asset Preparation & Validation
ansible-playbook -i inventory/hosts.yml playbooks/04_proxmox_templates.yml
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

All sensitive files, including private SSH keys (`credentials/ssh/*`), passwords, vault files (`.vault_pass`), `.env` files, and execution logs are strictly ignored by `.gitignore`. Secret scanning guards (`ggshield`) and YAML validators run automatically on every repository push.
