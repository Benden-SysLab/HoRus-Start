# Requirements

The active setup was tested with Debian 13 and Proxmox VE 9.2.21 on four nodes. The control host uses Debian WSL, Python 3, Ansible and OpenSSH.

The control host needs SSH access to each management IP. Workers need access to the master Proxmox API on TCP 8006. Nodes need working Corosync communication and consistent hostname resolution. Root credentials are required for first-time SSH bootstrap and joining workers; they are prompted at runtime.

The default management addresses are 10.255.0.7, 10.255.0.8, 10.255.0.9 and 10.255.0.10. Update both `inventory/hosts.yml` and `config/network.yml` if they change. Additional data disks and GPUs are not prerequisites for cluster formation.
