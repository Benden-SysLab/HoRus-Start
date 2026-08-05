# Backup & Restore Operations — HoRus-Start v2

---

## 1. What to Backup

To ensure full disaster recovery capability for your HoRus-Start environment, back up the following components:

### A. Declarative Configuration (`config/`)
Contains cluster, storage, network, and asset catalog definitions:
- `config/cluster.yml`
- `config/network.yml`
- `config/storage.yml`
- `config/image_catalog.yml`

### B. Control Node Local Credentials (`credentials/`)
- `credentials/proxmox_credentials.yml`
- `credentials/ssh/id_ed25519` and `id_ed25519.pub`
- `credentials/ssh/manifest.yml`

### C. Proxmox VE Cluster Configuration (`/etc/pve/`)
Back up cluster configuration files on Proxmox nodes:
- `/etc/pve/corosync.conf`
- `/etc/pve/storage.cfg`
- `/etc/pve/user.cfg`

---

## 2. Backup Procedure

### Local Backup Command
From the control node, generate a secure tar archive of configuration and credentials:

```bash
tar -czvf horus-start-backup-$(date +%Y%m%d).tar.gz config/ credentials/ inventory/
```

> 🔒 **Security Notice**: Encrypt the backup archive immediately if storing on external media:
> ```bash
> gpg -c horus-start-backup-$(date +%Y%m%d).tar.gz
> ```

---

## 3. Restore Procedure

1. **Unpack Backup Archive**:
   ```bash
   tar -xzvf horus-start-backup-20260805.tar.gz -C /path/to/HoRus-Start/
   ```

2. **Verify File Permissions**:
   Ensure SSH private keys maintain `0600` permissions:
   ```bash
   chmod 600 credentials/ssh/id_ed25519
   chmod 644 credentials/ssh/id_ed25519.pub
   ```

3. **Validate Schemas & Readiness**:
   ```bash
   python3 scripts/stage0_preflight.py
   python3 scripts/validate_schemas.py
   ```
