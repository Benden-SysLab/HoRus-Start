# Node & Cluster Disaster Recovery — HoRus-Start v2

---

## 1. Single Node Re-Join & Recovery

If a single cluster node experiences hardware failure or OS re-installation:

1. **Remove Failed Node from Cluster Quorum** (on surviving node):
   ```bash
   pvecm nodes
   pvecm delnode <FAILED_NODE_NAME>
   ```

2. **Re-provision Base OS**: Install fresh Debian 12/13 or Proxmox VE 8.x on the replacement node.

3. **Re-Run Stages 0 through 3**:
   Update `inventory/hosts.yml` and execute:
   ```bash
   python3 scripts/stage0_preflight.py
   ansible-playbook -i inventory/hosts.yml playbooks/00_bootstrap_connectivity.yml --limit <NODE_NAME>
   ansible-playbook -i inventory/hosts.yml playbooks/01_base_system_prep.yml --limit <NODE_NAME>
   ansible-playbook -i inventory/hosts.yml playbooks/02_proxmox_cluster.yml
   ```

---

## 2. Storage Re-Mount & Reconciliation Recovery

If storage drives are physically replaced or moved to new disk channels:

1. Update `config/storage.yml` with the new `/dev/disk/by-id/` disk IDs.
2. Execute Stage 4 in plan-only mode to audit expected modifications:
   ```bash
   ansible-playbook -i inventory/hosts.yml playbooks/03_storage_prepare.yml -e "storage_plan_only=true"
   ```
3. Execute Stage 4 provisioning to update mounts and Proxmox storage definitions cleanly:
   ```bash
   ansible-playbook -i inventory/hosts.yml playbooks/03_storage_prepare.yml
   ```

---

## 3. Quorum Break Recovery (Loss of Quorum)

If multiple nodes go offline and quorum is lost (`pvecm status` shows no quorum):

1. Force single-node quorum temporarily on surviving master node:
   ```bash
   pvecm expected 1
   ```
2. Repair cluster nodes and restart corosync:
   ```bash
   systemctl restart corosync pve-cluster
   ```
