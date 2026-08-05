# Secrets Management Policy — HoRus-Start v2

---

## 1. Secrets Classification

HoRus-Start classifies secrets into three tiers:

| Tier | Secrets Included | Storage Location | Protection Mechanism |
| :--- | :--- | :--- | :--- |
| **Tier 1 (Root Credentials)** | Root passwords for Proxmox target nodes | `credentials/proxmox_credentials.yml` | File permissions `0600`, strictly `.gitignore`'d |
| **Tier 2 (SSH Keys)** | Ed25519 private keys | `credentials/ssh/id_ed25519` | File permissions `0600`, strictly `.gitignore`'d |
| **Tier 3 (Runtime API Tokens)** | Proxmox API tokens (optional) | Local environment variables / vault | Memory / environment runtime |

---

## 2. Recommended Ansible Vault Integration

For multi-operator environments requiring tracked configuration, use **Ansible Vault** to encrypt `credentials/proxmox_credentials.yml`:

### Encrypting Credentials File
```bash
ansible-vault encrypt credentials/proxmox_credentials.yml
```

### Running Playbooks with Vault
```bash
ansible-playbook -i inventory/hosts.yml playbooks/00_bootstrap_connectivity.yml --ask-vault-pass
```

---

## 3. Secret Leakage Prevention Checklist

Before pushing changes to remote repositories:

- [x] Run `python3 scripts/stage0_preflight.py` to ensure local credentials are intact.
- [x] Verify `.gitignore` rules cover `credentials/*`, `*.pem`, `*.key`, `*.vault`, `.env`.
- [x] Run local secret scanning (e.g. `ggshield secret scan path .`).
