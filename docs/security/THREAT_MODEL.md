# Threat Model & Risk Assessment — HoRus-Start v2

---

## 1. System Boundaries & Assets

### Key Assets Protected
- Bare-metal hypervisor root access.
- Proxmox VE cluster quorum and network infrastructure.
- Physical storage drives and virtual disk volumes.
- Golden OS images and ISO catalog assets.

---

## 2. Threat Analysis & Mitigations

| Threat Vector | Potential Impact | Mitigation in HoRus-Start v2 |
| :--- | :--- | :--- |
| **Accidental Credential Leakage** | Unauthorized root SSH access to bare-metal nodes. | Mandatory `.gitignore` rules, `credentials/` folder isolation, CI secret scanning (`ggshield`). |
| **Accidental System OS Disk Overwrite** | Host OS corruption and loss of hypervisor during storage provisioning. | Stage 4 OS Safety Guard: formal check preventing `/` disk device formatting. |
| **Man-in-the-Middle (MitM) Attacks** | Interception of administrative sessions or image downloads. | Ed25519 SSH host key verification, SHA256 checksum validation on OS images. |
| **Corrupted Image Injection** | Compromised cloud image booted into virtual infrastructure. | `qemu-img info` integrity validation and checksum verification during Stage 5. |
| **Unauthorized Cluster Join** | Rogue node added to Corosync cluster mesh. | Corosync link encryption, dedicated SSH key auth, ring address binding. |
