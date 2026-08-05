# HoRus-Start — Runtime API v1 Specification

> **Version**: 1.0
> **Scope**: Cross-Stage Interface Contract & Storage Model

---

## 🌐 Overview

Runtime API v1 serves as the formal interface between execution stages. Instead of stages tightly coupling to Ansible variables or ad-hoc internal task results, all cross-stage communication occurs via versioned, validated JSON objects stored in `runtime/`.

---

## 📂 Structured Runtime Directory Layout

```
runtime/
├── discovery/   # Raw collected infrastructure data (PUBLIC)
│   ├── storage.json
│   └── pve_storage.json
├── facts/       # Normalized system facts (PUBLIC)
├── plans/       # Machine-readable execution plans (PUBLIC)
│   └── storage_plan.json
├── reports/     # Verification summaries & drift reports (PUBLIC)
│   ├── storage_drift.json
│   └── stage3.json
├── cache/       # Temporary reusable artifacts (INTERNAL)
├── locks/       # Execution synchronization locks (INTERNAL)
└── state/       # Persistent internal execution state (INTERNAL)
```

### Public vs Internal Runtime Objects

- **PUBLIC**: Consumed by future stages and external UI/CLI tools (`discovery/`, `facts/`, `plans/`, `reports/`). Immutable interface guarantees.
- **INTERNAL**: Used strictly inside an individual role or task execution (`cache/`, `locks/`, `state/`). Internal implementation details may evolve without breaking other stages.

---

## 🏷️ Mandatory Header Metadata Contract

All PUBLIC Runtime API v1 objects must contain the following top-level metadata fields:

```json
{
  "api_version": "v1",
  "schema_version": "1.0",
  "producer": "storage_prepare",
  "resource_type": "discovery",
  "stage": 3,
  "step": "discovery",
  "timestamp": "2026-07-30T15:00:00Z",
  "nodes": {}
}
```

### Metadata Fields
- `api_version`: Protocol version (`v1`).
- `schema_version`: Object schema version (`1.0`).
- `producer`: Stage or role name generating the object.
- `resource_type`: One of `discovery`, `facts`, `plan`, `report`.
- `stage`: Stage sequence number (0 to 8).
- `step`: Specific step name within the stage.
- `timestamp` / `generated_at`: ISO-8601 UTC timestamp.

---

## 🛡️ Validation & Schemas

Schemas are stored in `schemas/runtime/`:
- `schemas/runtime/discovery.schema.json`
- `schemas/runtime/storage.schema.json`
- `schemas/runtime/plan.schema.json`
- `schemas/runtime/report.schema.json`

Validate schema compliance using:
```bash
python3 scripts/validate_schemas.py
```
