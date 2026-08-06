# 05 — SRE Standard Package Catalog & Automation Use-Case Breakdown

Every package pre-installed into the HoRus Golden Templates (VM ID 9000, VM ID 9001, LXC templates) is chosen to satisfy specific operational, security, and automation requirements.

This document details the complete package manifest, explaining **why** each tool is included and where it is utilized across the automation lifecycle (Ansible, Terraform, Vault, Docker API, GitHub/Gitea API, Jenkins API).

---

## 🛠️ Complete Package Manifest & Justification Matrix

| Package Name | Functional Category | Specific Automation / API Use Case ("WHY") | Architectural Justification |
| :--- | :--- | :--- | :--- |
| **`qemu-guest-agent`** | Hypervisor Integration | **Proxmox VE API & Backup Hooks**: Reports guest IP addresses to Proxmox API (`/api2/json/nodes/{node}/qemu/{vmid}/agent/network-get-interfaces`), enables filesystem freeze during snapshots, handles graceful shutdown. | **Critical**. Allows Ansible and Proxmox API to discover VM IP address immediately upon boot without needing static ARP mappings. |
| **`openssh-server`** | Remote Administration | **Ansible Orchestration & Jenkins Agents**: Provides secure SSH daemon (`sshd`) for Ansible control nodes and Jenkins agents to connect and execute playbooks. | **Mandatory**. Primary remote control plane protocol for all Day-1/Day-2 configuration management. |
| **`openssh-client`** | Remote Connectivity | **Git & Rsync Operations**: Client SSH binaries (`ssh`, `scp`, `sftp`). Used by Ansible to clone private Git repositories (Gitea/GitHub over SSH) and transfer artifacts. | Required for secure inter-node transfers, Git deployments, and remote command delegation. |
| **`sudo`** | Privilege Delegation | **Ansible `become` Execution**: Enables `jenkins-srv` and `abbenden-srv` to execute root-privileged tasks (`sudo systemctl`, `sudo apt`) without logging in as `root`. | Core security control enforcing auditable privilege elevation. |
| **`curl`** | Network HTTP Client | **Vault API, Docker API, Gitea API, Jenkins API**: Used by bootstrap scripts and Ansible tasks to issue REST API queries (`curl -X POST https://vault.local/v1/auth/approle/login`). | Primary command-line HTTP/HTTPS client for API interactions and health check scripts. |
| **`wget`** | Network File Retrieval | **Binary Installer Downloading**: Downloads HashiCorp Vault/Terraform zip files, GitHub/Gitea release assets, and external scripts. | Non-interactive background download utility supporting recursive file grabs. |
| **`git`** | Version Control | **Ansible Pull & Infrastructure Repos**: Used by Ansible local playbooks to pull configuration state from Gitea/GitHub repositories. | Essential for GitOps execution, tracking local file changes, and managing infrastructure code. |
| **`vim`** | Text Editor | **Manual Debugging**: Full-featured modal editor for inspecting and editing configuration files during emergency maintenance. | Standard interactive text editor present on all Linux nodes. |
| **`btop`** | Resource Monitoring | **SRE Real-Time Diagnostics**: Interactive terminal UI showing live CPU, memory, disk I/O, network throughput, and process trees. | Superior diagnostic tool for visual troubleshooting of resource bottlenecks. |
| **`dnsutils`** | Network Diagnostics | **CoreDNS & Vault DNS Troubleshooting**: Contains `dig`, `nslookup`, and `host`. Used to test internal split-horizon DNS resolution (`dig @10.10.0.1 vault.service.consul`). | Essential for resolving microservice DNS routing and service discovery failures. |
| **`iproute2`** | Network Configuration | **Container & Network Routing**: Modern `ip` and `ss` commands used by Docker, Kubernetes CNI, and Ansible network modules. | Replaces legacy `net-tools`. Provides low-level socket and routing table inspection. |
| **`net-tools`** | Network Compatibility | **Legacy Diagnostics**: Provides `ifconfig` and `netstat` for compatibility with legacy diagnostic scripts. | Included for backwards compatibility with third-party tools and legacy scripts. |
| **`rsync`** | File Synchronization | **Ansible `synchronize` Module**: Used by Ansible to efficiently sync directory trees, deployment artifacts, and backup snapshots over SSH. | Delta-transfer algorithm drastically speeds up file deployments compared to standard `scp`. |
| **`ufw`** | Firewall Management | **Host Security Baseline**: Host-based firewall wrapper for `iptables`/`nftables`. Used by Ansible security roles to enforce port rules. | Simple declarative firewall interface for locking down node ingress/egress. |
| **`ca-certificates`** | PKI Security | **Infrastructure TLS Trust**: Common CA certificate bundle. Contains internal Root CA (`internal-ca.crt`). | Ensures system utilities (`curl`, `git`, `docker`, `apt`) trust internal HTTPS endpoints without `-k` bypasses. |
| **`gnupg2` & `gpgv`** | Cryptographic Signatures | **APT Package Verification**: GNU Privacy Guard used by `apt` on Debian 13 to verify GPG signatures of third-party repositories (Fluent Bit, Docker). | **Crucial for Debian 13**. Prevents `apt update` signature verification failures (`Missing key / verify signature`). |
| **`unzip` & `zip`** | Archive Utilities | **HashiCorp & Java Deployments**: Extraction tools for `.zip` archives. Used when installing HashiCorp binaries (Vault, Terraform, Consul) and Java WAR archives. | Standard compression utilities for unpacking vendor releases. |
| **`jq`** | JSON Processor | **Docker API, Vault API, Runtime API Processing**: Command-line JSON parser used in Bash scripts to extract tokens from API responses (`curl ... | jq -r .data.token`). | Essential for shell script automation, parsing `docker inspect` outputs, and handling JSON API payloads. |
| **`tree`** | Directory Visualization | **Workspace Inspection**: Displays directory layouts in depth-indented visual trees. | Helpful for visual verification of complex directory structures (e.g. `/etc/docker/`, `/var/log/`). |
| **`lsof`** | Process & Socket Audit | **Port Conflict Debugging**: Lists open files and active network sockets (`lsof -i :8080`). | Invaluable for identifying which process is blocking a network port during service startup failures. |
| **`fluent-bit`** | Log Forwarding | **Central Telemetry Forwarder**: Collects system logs (`/var/log/syslog`, `/var/log/journal/`, Docker logs) and streams them to central Loki/Elasticsearch pipelines. | Pre-installed and enabled as standard telemetry agent for shipping logs. |

---

## ❓ Why Pre-install Packages in Golden Images vs. Installing via Ansible Later?

1. **Boot Performance & Speed**: Pre-installing the SRE toolset reduces post-clone Ansible deployment time from **3–5 minutes** down to **less than 10 seconds**.
2. **Air-Gapped Reliability**: Instances deployed in isolated network segments can immediately execute Ansible playbooks and API calls without requiring outbound internet access.
3. **Deterministic Consistency**: Every VM created from Template 9000/9001 guarantees identical baseline package versions, eliminating environment drift across cluster nodes.
