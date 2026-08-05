# HoRus-Start — Infrastructure Domain Model Specification

> **Scope**: Domain Entities, Lifecycle, Ownership & Configuration Source

---

## 🧩 Domain Entities Overview

HoRus-Start transitions from simple scripts to a platform model operating on formal Infrastructure Domain Entities.

```
+-----------------------------------------------------------------------+
|                               Cluster                                 |
+-----------------------------------------------------------------------+
                                   |
            +----------------------+----------------------+
            |                                             |
         [ Node ]                                    [ Network ]
            |
    +-------+-------+
    |               |
 [ Disk ]       [ Storage ]
                    |
            +-------+-------+
            |               |
        [ Image ]      [ Template ]
            |               |
         [ VM ]          [ LXC ]
```

---

## 📋 Entity Specifications

### 1. Cluster
- **Description**: Proxmox VE quorum group spanning physical nodes (`horus-pmx-node01` through `node04`).
- **Owner**: Stage 3 (`proxmox_cluster`).
- **Source**: `inventory/hosts.yml`, `config/cluster.yml`.
- **Runtime File**: `runtime/facts/cluster.json`.

### 2. Node
- **Description**: Individual bare-metal server host running Proxmox VE hypervisor.
- **Owner**: Stage 2 (`base_system_prep`).
- **Source**: `inventory/hosts.yml`.
- **Runtime File**: `runtime/facts/nodes.json`.

### 3. Disk
- **Description**: Physical block device (`/dev/disk/by-id/...`) installed in a Node.
- **Owner**: Stage 4 (`storage_prepare` - Discovery) & Stage 0 (Auto-Discovery Gate).
- **Source**: Discovered dynamically via `lsblk` and `by-id`.
- **Runtime File**: `runtime/discovery/storage.json`.

### 4. Storage
- **Description**: Formatted and mounted filesystem registered as Proxmox VE directory volume.
- **Owner**: Stage 4 (`storage_prepare` - Provisioning).
- **Source**: `config/storage.yml`.
- **Runtime File**: `runtime/plans/storage_plan.json`, `runtime/reports/stage4.json`.

### 5. StorageTemplate
- **Description**: Pre-defined storage configuration profile (e.g. `local.yml`, `ceph.yml`, `nfs.yml`).
- **Owner**: Configuration Framework.
- **Source**: `config/storage_templates/`.

### 6. Image / Golden Image
- **Description**: Base operating system cloud image (Ubuntu, Debian, Alpine, RHEL).
- **Owner**: Stage 5 (`proxmox_templates`).
- **Source**: `config/templates.yml`, `artifacts/manifests/checksums.json`.

### 7. Template / VM Template
- **Description**: Prepared Proxmox VM template with Cloud-Init credentials and agent drivers.
- **Owner**: Stage 5 (`proxmox_templates`).

### 8. Platform Bootstrap
- **Description**: Management infrastructure control plane (`terraform-srv`, SSH keys, sudoers, API tokens, service accounts).
- **Owner**: Stage 6 (`platform_bootstrap`).

### 9. Security & Access Policy
- **Description**: Host security hardening (`sysctl`, `sshd`, `fail2ban`, `motd`, resource `limits`).
- **Owner**: Stage 7 (`security`).

### 10. Verification & Full Self-Test
- **Description**: Comprehensive platform self-test auditing Cluster, Storage, Images, Templates, Users, SSH, Security, and Reports.
- **Owner**: Stage 8 (`verification`).

### 11. Plan
- **Description**: Machine-readable action diff between Desired State (`config/`) and Discovered State (`runtime/discovery/`).
- **Owner**: Stage-specific Planners (e.g. `storage_plan.json`).

### 12. Operation / Report
- **Description**: Execution log, drift status, and health summary.
- **Owner**: Stage Verification tasks (`runtime/reports/`).
