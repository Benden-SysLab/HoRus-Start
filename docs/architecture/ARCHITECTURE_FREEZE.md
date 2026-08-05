# HoRus-Start — Architecture Stabilization & Freeze Specification (Pre-Stage 5)

> **Status**: STABLE & FROZEN
> **Effective Stage**: Pre-Stage 5 (Golden Image Factory)
> **Author / Architect**: HoRus Core Architecture Team

---

## 🏛️ Executive Summary

This document formally establishes the **Architecture Stabilization Milestone & Architecture Freeze** for the HoRus-Start Proxmox VE Infrastructure Platform prior to launching **Stage 5 (Golden Image Factory)**.

The architecture is **not** being refactored due to defects; rather, Stages 0 through 4 are fully operational, idempotent, and production-tested. This freeze establishes clear, immutable contracts between stages so future stages (Stage 5 Golden Image, Stage 6 Platform Bootstrap, Stage 7 Security, Stage 8 Verification) can be built independently without requiring architectural rewrites.

---

## 🔒 Objective 0: Frozen Components

The following architecture components are declared **STABLE AND FROZEN**:

1. **Stage 0 Readiness Gate (Mandatory Preflight)**:
   Stage 0 (`Infrastructure Readiness Gate & Auto-Discovery Assistant`) is the single non-destructive gatekeeper. No provisioning or state mutation is permitted unless Stage 0 reports `"status": "READY"`.
2. **Pipeline Architecture**:
   `Stage 0 Gate → Declarative Config → Discovery → Normalization → Planning → Provisioning → Verification → Reports`
3. **Runtime API v1 Contract**:
   JSON contracts with strict header metadata (`api_version: "v1"`, `schema_version: "1.0"`, `producer`, `resource_type`).
4. **Directory Layout**:
   - `config/` — Declarative desired state (Single Source of Truth for intent).
   - `runtime/` — Structured execution facts, plans, locks, caches, and reports.
   - `credentials/` — Local SSH keys and vault tokens (excluded from version control).
   - `artifacts/` — Local OS cloud images, templates, and SHA256 manifests.
   - `roles/` — Domain-driven Ansible roles.
   - `schemas/` — JSON schemas for config and runtime validation.
5. **Domain Entities**:
   Formal definitions for `Cluster`, `Node`, `Disk`, `Storage`, `StorageTemplate`, `Image`, `Template`, `VM`, `LXC`, `Network`, `Plan`, `Operation`, `Report`.

---

## 📜 Architectural Guarantees

- **No Mutation Without Verified Intent**: Stage 0 auto-generates templates for missing credentials or storage configurations, allowing user review before any execution.
- **No Backward Incompatibility**: Stage 5+ must consume public objects from **Runtime API v1**.
- **No Hidden Coupling**: Playbooks must not read private task variables or temporary files from prior stages.
- **Config vs Runtime Isolation**:
  - `config/` is the **ONLY** source of desired state.
  - `runtime/` is the **ONLY** source of actual/planned state.

---

## 📑 Linked Documentation

- [Stage 0 Readiness Gate Specification](./STAGE0_READINESS_GATE.md)
- [Runtime API v1 Specification](./RUNTIME_API_V1.md)
- [Domain Model Specification](./DOMAIN_MODEL.md)
- [Modular Planner Specification](./PLANNER_SPEC.md)

