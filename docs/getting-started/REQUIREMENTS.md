# System & Hardware Requirements — HoRus-Start v2

---

## 🖥️ Target Nodes Requirements

Each node in the Proxmox VE cluster must satisfy:

- **Hardware**: x86_64 architecture with Intel VT-x or AMD-V virtualization extensions enabled in BIOS/UEFI.
- **Operating System**: Clean installation of Debian 12 (Bookworm) or Proxmox VE 8.x.
- **Network**:
  - Minimum 1x 1Gbps Ethernet interface assigned a static IPv4 address.
  - Recommended: Dedicated 10Gbps mesh interface for Corosync cluster communication and storage sync.
- **Storage**:
  - OS Drive: 1x SSD/NVMe or HDD for system OS (`/`).
  - Data Drives: Additional physical block devices identified via `/dev/disk/by-id/` for storage reconciliation.

---

## 💻 Control Node Requirements

The machine orchestrating the bootstrap requires:

- **OS**: Linux (Debian, Ubuntu, RHEL) or macOS.
- **Python**: Python 3.10 or newer.
- **Ansible**: `ansible-core` 2.15+.
- **Network Reachability**: Direct IP connectivity to management IPs of all cluster nodes on SSH port 22.

---

## 🔒 Port & Protocol Requirements

| Port | Protocol | Usage | Direction |
| :--- | :--- | :--- | :--- |
| **22** | TCP | SSH Administration & Bootstrap | Control Node ➔ Target Nodes |
| **8006** | TCP | Proxmox VE Web GUI & API | Control Node ➔ Target Nodes |
| **5405-5412** | UDP | Corosync Cluster Quorum Communication | Node ⟷ Node (Mesh) |
| **22** | TCP | Ansible Inter-Node Mesh Communication | Node ⟷ Node |
| **80 / 443** | TCP | Outbound HTTP/HTTPS for APT updates and OS image downloads | Target Nodes ➔ Internet |
