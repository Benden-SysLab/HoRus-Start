# ADR-0003: Direct QEMU Guest Agent & Ansible Integration over Cloud-Init

## Status
**Accepted**

## Context
Many cloud environments use `cloud-init` to inject network configurations, SSH keys, and users at boot. However, `cloud-init` introduces additional boot delays (30–60s), fragile YAML metadata parsing, and potential race conditions with systemd networking services during initial boot.

## Decision
HoRus-Start adopts direct QEMU Guest Agent networking discovery and Ansible bootstrap execution, omitting `cloud-init`:
1. The QEMU Guest Agent (`qemu-guest-agent`) is pre-installed and enabled in all base templates.
2. The automation account (`jenkins-srv`) and its Ed25519 public SSH key are baked directly into the template.
3. DHCP assigns the initial IP address, which is reported directly to the Proxmox API via QEMU Agent (`/api2/json/nodes/{node}/qemu/{vmid}/agent/network-get-interfaces`).
4. Terraform and Ansible query the Proxmox API to retrieve the assigned IP and initiate configuration immediately.

## Consequences
### Positive
- Instantaneous boot without cloud-init execution delays or YAML injection errors.
- Simplifies template creation and reduces guest dependencies.

### Negative
- Requires a DHCP server active on the provisioning network during initial boot.
