# 16 — Template Versioning & Naming Conventions

To maintain order across virtual machine templates and prevent ambiguity during Day-1 Terraform or Ansible provisioning, **HoRus-Start** enforces a strict versioning and naming scheme for all Proxmox VE templates.

---

## 🏷️ Versioning Scheme Architecture

A Golden Template name combines the **VM ID**, **Distribution Name**, **Template Archetype**, and **Semantic Build Date Version**:

```
[ VM ID ] - [ OS Distribution ] - [ Archetype ] - [ Version Tag ]
  9000    -   debian-13       -    base       -   v2026.08
  9001    -   debian-13       -    docker     -   v2026.08
```

---

## 📋 Proxmox VE Template Name Mapping Table

| VM ID | Template Name | OS / Release | Archetype | Active Version Tag |
| :--- | :--- | :--- | :--- | :--- |
| `9000` | `debian-13-trixie-base-v2026.08` | Debian 13 (Trixie) | SRE Base | `v2026.08` |
| `9001` | `debian-13-trixie-docker-v2026.08` | Debian 13 (Trixie) | Docker Engine | `v2026.08` |
| `9010` | `ubuntu-2404-noble-base-v2026.08` | Ubuntu 24.04 LTS | SRE Base | `v2026.08` |
| `9020` | `rocky-9-minimal-base-v2026.08` | Rocky Linux 9 | SRE Base | `v2026.08` |
| `9030` | `almalinux-9-minimal-base-v2026.08` | AlmaLinux 9 | SRE Base | `v2026.08` |
| `9050` | `tpl-debian-13-lxc-v2026.08` | Debian 13 (LXC) | LXC Base | `v2026.08` |
| `9090` | `win2025-std-base-v2026.08` | Windows Server 2025 | WinRM Base | `v2026.08` |

---

## 📄 In-Guest Version Metadata File (`/etc/horus-template-release`)

Every Linux template embeds a version release file at `/etc/horus-template-release` allowing Ansible playbooks and runtime inspection scripts to verify the active template build:

```ini
HORUS_TEMPLATE_ID="9001"
HORUS_TEMPLATE_NAME="debian-13-trixie-docker"
HORUS_BUILD_VERSION="v2026.08"
HORUS_BUILD_DATE="2026-08-06"
HORUS_BUILD_ENGINEER="abbenden-srv"
HORUS_STAGE_ORIGIN="Stage 5 Asset Preparation"
```
