# 17 — Infrastructure Lifecycle Integration & End-to-End Pipeline

**HoRus Templates** do not exist in isolation. They form the foundational bridge between Day-0 bare-metal cluster bootstrapping and Day-1/Day-2 application orchestration in the **HoRus-Start** framework (see [21-day0-day1-day2.md](./21-day0-day1-day2.md)).

This document illustrates the end-to-end position of the **HoRus Template Factory** within the complete **Infrastructure Lifecycle**.

---

## 🗺️ End-to-End Infrastructure Lifecycle Flow

```mermaid
flowchart TD
    subgraph Day0 ["DAY 0: Bare-Metal Cluster Bootstrapping"]
        Stage0[Stage 0: Pre-Flight & Network Verification] --> Stage1[Stage 1: Proxmox VE OS & Hypervisor Setup]
        Stage1 --> Stage2[Stage 2: Storage Infrastructure & ZFS/LVM]
        Stage2 --> Stage3[Stage 3: Network Topology & Bridges]
        Stage3 --> Stage4[Stage 4: Storage Pool Registration]
        Stage4 --> Stage5[Stage 5: Asset Catalog Downloads]
    end

    subgraph Factory ["HORUS TEMPLATE FACTORY BOUNDARY"]
        Stage5 --> BuildVM[Build Candidate VM 9000 Base / 9001 Docker]
        BuildVM --> AuditCheck[Run Audit Engine Rules: 18-audit.md]
        AuditCheck --> Freeze[Convert to Proxmox Read-Only Template]
    end

    subgraph Day1 ["DAY 1: Provisioning & Orchestration"]
        Freeze --> TF[Terraform: Instantaneous Clone VM 9000/9001]
        TF --> QEMU[Boot & QEMU Guest Agent IP Discovery]
        QEMU --> Ansible[Ansible Orchestration as jenkins-srv]
        Ansible --> AcceptTest[Automated Acceptance Testing]
    end

    subgraph Day2 ["DAY 2: Operations & Maintenance"]
        AcceptTest --> FluentBit[Fluent Bit Log Aggregation]
        FluentBit --> Metrics[Prometheus Performance Monitoring]
        Metrics --> PBS[Proxmox Backup Server Snapshots]
        PBS --> ProdWorkload[Active Production Workload Execution]
    end
```

---

## 🔗 Interface Boundaries & Handoff Points

1. **Stage 5 ➔ Template Factory**: Stage 5 downloads the ISOs and LXC tarballs into `storage-infra/template/iso/`. The engineer or pipeline builds candidate templates using these downloaded assets.
2. **Template Factory ➔ Terraform Provisioning**: Terraform consumes template IDs `9000`, `9001`, or `9050` using the Proxmox Provider (`bpg/proxmox` or `telmate/proxmox`), performing full clones on local storage in seconds.
3. **Terraform ➔ Ansible Orchestration**: Once Terraform clones a VM and boots it, Ansible reads the VM's IP address reported by the QEMU Guest Agent via the Proxmox API, connects immediately as `jenkins-srv`, and configures the production role. See [ADR-0003](../adr/ADR-0003-no-cloud-init.md).
