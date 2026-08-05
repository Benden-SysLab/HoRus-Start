# HoRus-Start — Modular Planner Architecture Specification

> **Scope**: Specialized Planners, Reconciliation Engine & Execution Workflows

---

## ⚙️ Modular Planner Concept

To prevent the Planning stage from growing into an unmaintainable monolith, HoRus-Start decouples execution planning into **Specialized Modular Planners**.

Each Modular Planner follows a pure reconciliation model:

```
[ Desired State ] (config/*.yml)
        +
[ Actual State ] (runtime/discovery/*.json)
        │
        ▼
[ Modular Planner ] ──► Generates Machine-Readable Plan (runtime/plans/*.json)
        │
        ▼
[ Interactive Authorization / Dry-Run Check ]
        │
        ▼
[ Safe Provisioning Engine ]
```

---

## 🗂️ Specialized Modular Planners

1. **Storage Planner** (Stage 4 — `roles/storage_prepare/tasks/03_validation.yml`)
   - Inputs: `config/storage.yml` + `runtime/discovery/storage.json`.
   - Output: `runtime/plans/storage_plan.json`.
   - Actions: Calculates `needs_format`, `needs_mkdir`, `needs_fstab`, `needs_mount`, `needs_pvesm_add`, `needs_umount`.

2. **Image Planner** (Stage 5 — `proxmox_templates`)
   - Inputs: `config/templates.yml` + `runtime/discovery/images.json` + `artifacts/manifests/checksums.json`.
   - Output: `runtime/plans/image_plan.json`.
   - Actions: Calculates image downloads, hash checks, and template conversion.

3. **Platform Bootstrap Planner** (Stage 6 — `platform_bootstrap`)
   - Inputs: `config/platform.yml` + `runtime/discovery/platform.json`.
   - Output: `runtime/plans/platform_plan.json`.
   - Actions: Plans management infrastructure (terraform-srv, SSH keys, sudoers, API tokens, service accounts).

4. **Security Planner** (Stage 7 — `security`)
   - Inputs: `config/security.yml` + `runtime/discovery/security.json`.
   - Output: `runtime/plans/security_plan.json`.
   - Actions: Plans hardening rules (sysctl parameters, sshd hardening, fail2ban, motd banners, limits).

5. **Verification Engine** (Stage 8 — `verification`)
   - Inputs: All stage execution states & system discovery data.
   - Output: `runtime/reports/stage8.json`.
   - Actions: Executes a comprehensive self-test (Cluster, Storage, Images, Templates, Users, SSH, Security, Reports).

6. **Cluster Planner** (Stage 3 — `proxmox_cluster`)
   - Inputs: `config/cluster.yml` + `runtime/discovery/cluster.json`.
   - Output: `runtime/plans/cluster_plan.json`.

---

## 🔒 Safety Rules for Planners

1. **Never mutate during planning**: Planners are read-only and must never format, mount, create, or delete resources.
2. **Explicit Operator Authorization**: Every plan must support dry-run preview (`storage_plan_only=true`) and interactive prompt approval.
3. **OS System Disk Protection**: Safety assertions must strictly block formatting or mounting operations on OS root (`/`), `/boot`, `/boot/efi`, `/etc/pve`, `/var`, or `/usr`.
