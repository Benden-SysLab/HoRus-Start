# HoRus-Start — Stage 0: Infrastructure Readiness Gate Specification

> **Stage Status**: STABLE & MANDATORY GATEWAY
> **Effective Version**: 1.0 (Pre-Stage 4 Freeze)

---

## 🏛️ Concept & Purpose

**Stage 0 (Infrastructure Readiness Gate)** serves as the non-destructive entry point and auto-discovery assistant for the HoRus-Start platform. It guarantees that no infrastructure mutation (formatting, partitioning, cluster joining, template creation) can take place until the environment, credentials, node connectivity, storage devices, and artifacts are fully verified.

If required user configurations (e.g. `credentials/proxmox_credentials.yml` or `config/storage.yml`) are missing, Stage 0 **does not crash blindly**. Instead, it generates commented template files pre-filled with discovered hardware details (e.g., persistent `/dev/disk/by-id/` disk identifiers) and safely prompts the user for necessary inputs before execution can proceed.

---

## ⚙️ Core Sub-modules

### 0.1 Credentials Bootstrap & Validation
- **Path**: `credentials/proxmox_credentials.yml`, `credentials/ssh/`
- **Behavior**:
  - Checks for required password/token credentials.
  - If missing, creates a secure, commented template with clear `# REQUIRED` markers and sets safe file permissions (`0600`).
  - Automatically generates ed25519 SSH keys if missing in `credentials/ssh/` (self-healing, non-blocking).
  - Validates key permissions and syntax.

### 0.2 Node Connectivity & Privilege Audit
- **Behavior**:
  - Validates network reachability (ICMP ping & TCP/22).
  - Tests SSH authentication across cluster nodes (`horus-pmx-node01` through `node04`).
  - Confirms root/sudo execution privileges without state mutation.

### 0.3 Storage Hardware Auto-Discovery (READ-ONLY)
- **Behavior**:
  - Discovers all physical block devices via `/dev/disk/by-id/`.
  - Filters out OS system root drives (`/`, `/boot`, `/boot/efi`, `/etc/pve`).
  - If `config/storage.yml` is missing or empty, Stage 0 generates a customized `config/storage.yml` populated with discovered drive serial numbers, disk sizes, and recommended mount configurations as commented guidance.

### 0.4 Artifact & Cloud Image Preflight
- **Path**: `artifacts/images/`, `artifacts/manifests/checksums.json`
- **Behavior**:
  - Inspects required OS cloud images (Debian 13, Ubuntu 24.04, Alpine).
  - Validates file sizes and SHA256 checksums against manifest files.
  - Generates `runtime/preflight/artifacts.json` to prevent Stage 4 from attempting downloads or operations on corrupted images.

### 0.5 Readiness Report Generation
- **Path**: `runtime/reports/stage0.json`
- **Behavior**:
  - Aggregates preflight status: `READY`, `WAITING_USER_INPUT`, or `FAILED`.
  - Serves as the blocking gatekeeper for all downstream Ansible playbooks.

---

## 🔒 Mandatory Rule

> **Immutable Rule**: No provisioning stage (Stage 1 through Stage 7) may execute unless Stage 0 Readiness Gate has completed successfully and produced a valid `stage0.json` report with `"status": "READY"`.
