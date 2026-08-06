# 21 — Day-0 / Day-1 / Day-2 Operational Lifecycle Framework

The **HoRus Template Factory** structures infrastructure operations into three distinct, non-overlapping phases: **Day 0**, **Day 1**, and **Day 2**.

---

## 🗺️ Day-0 / Day-1 / Day-2 Architecture Flow

```mermaid
flowchart TD
    subgraph Day0 ["DAY 0: Cluster & Template Bootstrapping"]
        Stage0[Stage 0: Network & SSH Pre-flight] --> Stage1[Stage 1: PVE Hypervisor Installation]
        Stage1 --> Stage2[Stage 2: Storage Infrastructure]
        Stage2 --> Stage3[Stage 3: Network Bridges & SDN]
        Stage3 --> Stage4[Stage 4: Storage Registration]
        Stage4 --> Stage5[Stage 5: Asset Catalog Downloads]
        Stage5 --> Factory[HoRus Template Factory: Build VM 9000/9001]
    end

    subgraph Day1 ["DAY 1: Provisioning & Orchestration"]
        Factory --> TF[Terraform: Clone VM 9000/9001 in 5s]
        TF --> Boot[VM Boot & QEMU Agent IP Discovery]
        Boot --> Ansible[Ansible Playbook Orchestration as jenkins-srv]
        Ansible --> Test[Acceptance Verification & Smoke Tests]
    end

    subgraph Day2 ["DAY 2: Operations & Maintenance"]
        Test --> Telemetry[Fluent Bit Central Log Shipping]
        Telemetry --> Metrics[Prometheus Performance Monitoring]
        Metrics --> Backup[PBS Proxmox Backup Snapshots]
        Backup --> Lifecycle[Security Patching & Template Rebuild Cycle]
    end
```

---

## 📋 Operational Phase Responsibilities

### Day 0: Bare-Metal Bootstrapping & Template Factory
- **Goal**: Transform bare-metal hardware into an operational Proxmox cluster and build frozen, SRE-hardened OS templates (`VM ID 9000+`).
- **Tooling**: HoRus-Start Ansible Playbooks (Stages 0–5) & HoRus Template Factory assembly.
- **Output**: Functional Proxmox VE cluster with `storage-infra` holding ready-to-clone templates.

### Day 1: Automated Provisioning & Configuration
- **Goal**: Instantiate new virtual machines or LXC containers for specific application workloads.
- **Tooling**: Terraform Proxmox Provider + Ansible Configuration Management.
- **Output**: Fully configured microservices (Vault, Harbor, Gitea, Jenkins) running on cloned instances.

### Day 2: Production Operations & Lifecycle Maintenance
- **Goal**: Maintain system health, monitor performance, collect logs, manage backups, and execute zero-downtime template updates.
- **Tooling**: Fluent Bit, Prometheus, Proxmox Backup Server (PBS), and Template Rebuild Pipeline.
- **Output**: High-availability, self-healing infrastructure.
