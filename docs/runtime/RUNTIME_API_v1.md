# HoRus-Start Runtime API v1 & Pipeline v1.0 Contract Specification

## Overview

The **HoRus-Start Runtime API v1** defines a standardized, machine-readable contract interface for the entire infrastructure provisioning lifecycle. By separating infrastructure execution (Ansible/Proxmox) from execution state observability, external components—such as Web UIs, REST APIs, CLI orchestrators, or automated CI/CD runners—can inspect, monitor, pause, and resume provisioning workflows without tight coupling to Ansible internal details.

---

## 1. Pipeline v1.0 State Machine Architecture

Stage 5 (Golden Image & Template Factory) is structured as a **sequential, idempotent pipeline** with clear stage boundaries:

```
[5.1 Discovery] ──► [5.2 Planning] ──► [5.3 Asset Catalog] ──► [5.3.5 Image Customizer] ──► [5.4 VM Factory] ──► [5.5 LXC Factory] ──► [5.6 Verification] ──► [5.7 Reporting]
```

### Stage Responsibilities & Platform Independence

1. **Stage 5.1 — Discovery (`discovery.json`)**:
   - Inspects existing local & cluster resources (cloud images, ISOs, drivers, LXC templates).
   - Generates discovery caches in `runtime/discovery/`.

2. **Stage 5.2 — Runtime Planning (`planning.json`)**:
   - Calculates missing assets, checksum requirements, and required downloads.

3. **Stage 5.3 — Asset Catalog Publisher (`asset_catalog.json`)**:
   - Downloads, verifies integrity, and publishes external artifacts into `assets/` and `template/iso/`.
   - **Platform-Independent**: Contains zero Proxmox/Hypervisor logic (no `qm`, `pct`, or `pveam` calls).
   - Exit State: `ASSET_CATALOG_READY`.

4. **Stage 5.3.5 — Image Customization Factory (`image_customization.json`)**:
   - Bakes raw vendor cloud images (e.g. `debian-13-genericcloud-amd64.qcow2`) into optimized base OS images inside `factory/qcow2/debian13-horus-base.qcow2`.
   - Installs base SRE packages (`qemu-guest-agent`, `cloud-init`, `sudo`, `curl`, `wget`, `git`, `vim`, `htop`, `tmux`, `jq`, `rsync`, `python3`, `chrony`).
   - Writes `/etc/horus/` metadata (`image-version`, `build-date`, `image-role`).
   - Configures UTC timezone, locale, SSH hardening, and clears `machine-id`/cloud-init state for clean cloning.
   - Exit State: `IMAGE_CUSTOMIZED_READY`.

5. **Stage 5.4 — Golden VM Factory (`vm_factory.json`)**:
   - Instantiates Proxmox VM templates (`qm create`, `qm importdisk`, Cloud-Init configuration, `qm template`) using customized `debian13-horus-base.qcow2`.
   - Exit State: `VM_FACTORY_READY`.

6. **Stage 5.5 — LXC Template Factory (`lxc_factory.json`)**:
   - Downloads and manages Proxmox LXC container templates (`pveam download`, template cache).
   - Exit State: `LXC_FACTORY_READY`.

7. **Stage 5.6 — Verification (`verification.json`)**:
   - Validates template integrity, storage allocation, and multi-node cluster synchronization.
   - Exit State: `VERIFIED`.

8. **Stage 5.7 — Reporting (`stage5.json`)**:
   - Produces machine-readable aggregator reports and final status state (`SUCCESS`).

---

## 2. Standardized Report Object Schema

Every stage report and aggregator object generated under Runtime API v1 adheres to the following JSON schema specification:

```json
{
  "api_version": "v1",
  "schema_version": "1.0",
  "pipeline_version": "1.0",
  "execution_id": "202608041400-9182",
  "producer": "ansible_stage5_golden_image_factory",
  "resource_type": "report",
  "stage": 5,
  "current_stage": "asset_catalog",
  "status": "ASSET_CATALOG_READY",
  "completed": [
    "discovery",
    "planning",
    "asset_catalog"
  ],
  "pending": [
    "vm_factory",
    "lxc_factory",
    "verification",
    "reporting"
  ],
  "executed_at": "2026-08-04T14:10:00Z",
  "timestamps": {
    "started_at": "2026-08-04T14:00:00Z",
    "updated_at": "2026-08-04T14:10:00Z",
    "completed_at": null
  },
  "dry_run": false,
  "health": {
    "state": "healthy",
    "warnings": 0,
    "errors": 0,
    "status": "ASSET_CATALOG_READY",
    "builder_node": "horus-pmx-node03",
    "factory_storage": "storage-infra"
  },
  "nodes": {
    "horus-pmx-node03": {
      "builder_node": "horus-pmx-node03",
      "storage": "storage-infra"
    }
  }
}
```

### Key Field Definitions

- **`api_version`**: API contract version (`"v1"`).
- **`schema_version`**: JSON Schema structure version (`"1.0"`).
- **`pipeline_version`**: Version of the workflow pipeline (`"1.0"`).
- **`execution_id`**: Unique execution run identifier correlating all report artifacts produced during a single run.
- **`current_stage`**: The exact pipeline stage currently executing or recently completed (`"discovery"`, `"planning"`, `"asset_catalog"`, `"image_customization"`, `"vm_factory"`, `"lxc_factory"`, `"verification"`, `"reporting"`).
- **`status`**: Workflow status state (`DISCOVERY_READY`, `PLANNING_READY`, `ASSET_CATALOG_READY`, `IMAGE_CUSTOMIZED_READY`, `VM_FACTORY_READY`, `LXC_FACTORY_READY`, `VERIFIED`, `IN_PROGRESS`, `SUCCESS`, `FAILED`).
- **`completed`**: Ordered list of successfully completed sub-stages.
- **`pending`**: Ordered list of remaining sub-stages.
- **`timestamps`**: ISO-8601 timestamps tracking start, last update, and completion.
- **`health`**: Execution health container separated from pipeline status:
  - `state`: `"healthy"`, `"warning"`, or `"error"`.
  - `warnings`: Counter of non-fatal warnings (e.g. background downloader in progress).
  - `errors`: Counter of fatal failures.

---

## 3. Runtime Artifact Directory Structure

All runtime artifacts are written to `runtime/` locally and mirrored to `{{ factory_base_dir }}/runtime/` on the Master Builder Node for cluster observability:

```
runtime/
├── discovery/
│   ├── storage.json
│   ├── cloud_images.json
│   ├── iso_catalog.json
│   ├── driver_catalog.json
│   └── manual_assets.json
├── plans/
│   └── storage_plan.json
└── reports/
    ├── discovery.json           # Stage 5.1 Report
    ├── planning.json            # Stage 5.2 Report
    ├── asset_catalog.json       # Stage 5.3 Report
    ├── image_customization.json # Stage 5.3.5 Report
    ├── vm_factory.json          # Stage 5.4 Report
    ├── lxc_factory.json         # Stage 5.5 Report
    ├── verification.json        # Stage 5.6 Report
    ├── image_factory.json       # Stage 5.7 Detailed Catalog Report
    ├── template_validation.json  # Stage 5.7 Node Sync Report
    └── stage5.json              # Stage 5 Aggregator Pipeline Report
```

---

## 4. Idempotency & Failure Recovery

1. **Decoupled Downloads**: If Stage 5.4 or 5.5 fails (e.g., due to temporary hypervisor lock or API timeout), Stage 5.3's downloaded assets remain valid and fully published in `assets/` and `template/iso/`.
2. **Resumption**: Subsequent runs skip downloading existing valid assets and immediately resume from Stage 5.4 (`VM Factory`) or Stage 5.5 (`LXC Factory`).
3. **Builder Node Observability**: Every state update is automatically synchronized to the Master Builder Node, allowing cluster nodes to inspect pipeline progress in real-time.
