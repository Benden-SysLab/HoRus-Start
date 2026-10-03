# Troubleshooting

## SSH bootstrap

If password authentication fails, check the root password entered in the terminal, SSH reachability and the node's `PermitRootLogin` policy. If key authentication fails, verify `HORUS_SSH_KEY_DIR` and the key pair, then try `ssh -i "$HORUS_SSH_KEY_DIR/horus-pmx-cluster" root@10.255.0.7`. Do not copy a private key into the repository.

## APT sources

Stage 01 manages Debian Trixie sources in `/etc/apt/sources.list` and the Proxmox no-subscription source in `/etc/apt/sources.list.d/proxmox.sources`. If updates fail, inspect `apt-cache policy` and the files under `/etc/apt/sources.list.d/` before rerunning Stage 01.

## Cluster join and quorum

Use `pvecm status` and `pvecm nodes` on each node. The expected cluster is `HoRus-SysLab` with four members and `Quorate: Yes`. Check TCP 8006 from workers to the master, hostname resolution and `journalctl -u corosync -u pveproxy -u pvedaemon --no-pager -n 100`. A first-time API join may ask to trust the master's TLS certificate; the playbook handles this prompt. Worker joins run one at a time. An existing member is skipped on rerun.

Do not remove `/etc/pve/corosync.conf` or reset a partially formed cluster merely because a playbook failed. First inspect actual membership and the failed task.

## Reports

`runtime/reports/stage0.json`, `stage1.json` and `stage2.json` are local execution artifacts. Run `python3 scripts/validate_schemas.py` to validate existing reports. A report from an earlier run may be stale; check its timestamp.
