# ADR-0001: HoRus Template Factory Architecture

## Status
**Accepted**

## Context
Provisioning new virtual machines or LXC containers by booting clean ISOs and downloading hundreds of packages over WAN during instance initialization leads to long provisioning times (3–5+ minutes), high failure rates due to mirror downtime, and configuration drift across cluster nodes.

## Decision
We establish the **HoRus Template Factory** pattern. Operating system virtual machines and LXC containers are pre-assembled, SRE-hardened, tested, sterilized, and converted into read-only Proxmox VE templates (`VM ID 9000+`). 

Day-1 provisioning tools (Terraform/Ansible) perform instantaneous disk clones off these pre-baked templates.

## Consequences
### Positive
- Instantiation time drops from minutes to **3–10 seconds** per VM.
- 100% deterministic reproducibility across cluster nodes without network drift.
- Pre-baked automation credentials (`jenkins-srv`) allow immediate Ansible execution upon first boot.
- Internal Root CA is pre-trusted across all cloned nodes.

### Negative
- Requires a manual or automated template rebuilding cycle when OS security updates or package major versions are released.
