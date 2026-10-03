# HoRus-Start

[English](README.md) · [Русский](README.ru.md) · [Українська](README.uk.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [日本語](README.ja.md)

Ansible bootstrap for the four-node **HoRus-SysLab** Proxmox VE cluster. The active pipeline prepares SSH access, standardizes Debian/Proxmox APT repositories and base packages, then forms and verifies the cluster. It was run against Debian 13 and Proxmox VE 9.2.21.

| Node | Management IP | Cluster role |
| --- | --- | --- |
| horus-pmx-node01 | 10.255.0.7 | initial cluster node |
| horus-pmx-node02 | 10.255.0.8 | joining node |
| horus-pmx-node03 | 10.255.0.9 | joining node |
| horus-pmx-node04 | 10.255.0.10 | joining node |

## Run from WSL Debian

Install Python 3 and Ansible on the control machine. Make sure it can reach all four nodes over SSH and that the nodes can reach the master API on TCP 8006 and one another over Corosync. Review `inventory/hosts.yml`, `config/network.yml` and `config/cluster.yml` before running.

```bash
cd /path/to/HoRus-Start
export HORUS_SSH_KEY_DIR=/mnt/c/Users/Benden/.ssh/horus/horus-pmx-node

python3 scripts/stage0_preflight.py
ansible-playbook -i inventory/hosts.yml playbooks/00_bootstrap_connectivity.yml
ansible-playbook -i inventory/hosts.yml playbooks/01_base_system_prep.yml
ansible-playbook -i inventory/hosts.yml playbooks/02_proxmox_cluster.yml
```

Stage 0 generates the external Ed25519 key pair on first run and writes `runtime/reports/stage0.json`. Stage 00 prompts for node root passwords in the terminal, deploys the public key and verifies SSH. Stage 01 replaces legacy APT sources with Debian Trixie and Proxmox no-subscription sources, upgrades packages and writes `stage1.json`. Stage 02 creates/joins the cluster sequentially, verifies Corosync/quorum on every node and writes `stage2.json`. Existing members are skipped on reruns. The master root password is requested only if a worker needs joining.

`./horus-start` runs Stage 0 and the SSH bootstrap. `playbooks/site.yml` runs the three Ansible playbooks; run Stage 0 separately before it on a new control machine.

The SSH private key stays outside Git. By default its directory is `~/.ssh/horus/horus-pmx-node`; set `HORUS_SSH_KEY_DIR` in WSL to point to the Windows key directory. The default key name is `horus-pmx-cluster`; `HORUS_SSH_KEY_NAME` can override it. Passwords are prompted at runtime and are not stored in repository YAML.

## Scope

Disk formatting, mounts, Proxmox storage registration, GPU/PCI passthrough, VM templates and application deployment are handled separately. This repository does not configure them. Do not treat a successful cluster run as a storage or GPU readiness check.

Local reports are under `runtime/reports/` and are ignored by Git. Validate generated reports with `python3 scripts/validate_schemas.py`. For details see [installation](docs/getting-started/INSTALLATION.md), [quickstart](docs/getting-started/QUICKSTART.md) and [troubleshooting](docs/operations/TROUBLESHOOTING.md).
