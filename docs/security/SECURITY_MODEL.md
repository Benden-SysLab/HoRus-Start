# Security Model — HoRus-Start v2

---

## Executive Overview

**HoRus-Start v2** implements a defense-in-depth security model designed specifically for bare-metal hypervisor cluster provisioning. Security controls are enforced at every pipeline boundary, starting with local credential isolation and automated secret scanning.

---

## Core Security Principles

### 1. Zero Credentials in Version Control
- All cleartext passwords, API tokens, and private SSH keys are stored exclusively inside `credentials/`.
- The `.gitignore` policy strictly excludes all sensitive files from git tracking.
- Automated pre-commit and CI workflows run **GitGuardian (`ggshield`)** secret scanning to detect key leakage before commits enter the repository.

### 2. Local SSH Identity Isolation
- SSH keys (`ed25519`) are generated locally on the administrator control node during Stage 1.
- Private SSH keys never leave the control node.
- Public keys are distributed to target node `~root/.ssh/authorized_keys` via encrypted Ansible transports.

### 3. Isolated Runtime Execution State
- Execution facts, hardware discovery records, plans, and reports are written exclusively to `runtime/`.
- `runtime/` is strictly isolated and git-ignored, preventing operational telemetry or system metadata from leaking into public code.

### 4. Gate 0 Security Verification
- Stage 0 (`scripts/stage0_preflight.py`) acts as a blocking security gate.
- It validates password formats, checks for empty or default credentials, and aborts execution before any cluster or network modifications occur.

### 5. First Security Gate Verified (v2.0-RC1 Baseline)
- **Status**: PASSED
- All cleartext keys removed from repository history.
- CI pipeline integrated with secret scanning guards.
- Security baseline enforced across all Stage 0–5 roles.
