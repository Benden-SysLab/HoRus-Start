# Installation

Run the playbooks from Debian in WSL or another Linux control host. The working setup uses Debian WSL, Python 3 and Ansible. Install `ansible-core` and OpenSSH (`ssh`, `ssh-keygen`) using your usual package manager; Ansible's `expect` task needs `python3-pexpect` on joining Proxmox nodes. Stage 01 installs that package.

Clone the repository, then review `inventory/hosts.yml`, `config/network.yml` and `config/cluster.yml`. The checked-in inventory targets 10.255.0.7–10.255.0.10. If the addresses change, update both inventory and network configuration before running any playbook.

For the Windows key directory, set this variable in WSL:

```bash
export HORUS_SSH_KEY_DIR=/mnt/c/Users/Benden/.ssh/horus/horus-pmx-node
```

The default key name is `horus-pmx-cluster`. Run `python3 scripts/stage0_preflight.py` to generate it if absent. On WSL, verify the key can be read by OpenSSH; Windows-mounted files may require suitable permissions. The private key must stay outside Git. Root passwords are entered at runtime in the terminal.

Then follow [Quickstart](QUICKSTART.md). Generated reports are under `runtime/reports/`.
