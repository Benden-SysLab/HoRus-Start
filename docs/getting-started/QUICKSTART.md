# Quickstart

Run these commands from the repository root in WSL Debian after reviewing the inventory and key path:

```bash
export HORUS_SSH_KEY_DIR=/mnt/c/Users/Benden/.ssh/horus/horus-pmx-node
python3 scripts/stage0_preflight.py
ansible-playbook -i inventory/hosts.yml playbooks/00_bootstrap_connectivity.yml
ansible-playbook -i inventory/hosts.yml playbooks/01_base_system_prep.yml
ansible-playbook -i inventory/hosts.yml playbooks/02_proxmox_cluster.yml
python3 scripts/validate_schemas.py
```

The SSH bootstrap prompts for node root passwords. The cluster playbook prompts for the master root password only when a worker must join. It joins workers sequentially and verifies quorum on all four nodes. To inspect the result on a Proxmox node, run `pvecm status` and `pvecm nodes`.

`./horus-start` combines preflight and SSH bootstrap. `playbooks/site.yml` combines the three Ansible playbooks; Stage 0 must be run separately first.

Disk storage, GPU passthrough and VM templates are outside this pipeline.
