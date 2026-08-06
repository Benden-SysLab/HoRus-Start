# 07 — SSH Security & Key Management Guide

This document covers SSH key management, directory ACLs, permissions mechanics, and troubleshooting PowerShell quirks during key deployment.

---

## 🔒 SSH File Permissions Standard

The OpenSSH daemon (`sshd`) strictly enforces security permissions on user home directories, `.ssh` folders, and `authorized_keys` files. If permissions are too permissive (e.g. group or world-writable), `sshd` rejects public key authentication with `Permission denied (publickey)`.

### Required File Permission Matrix

```
/home/<username>/
├── .ssh/                    <-- Mode: 700 (drwx------) Owned by <username>:<username>
│   └── authorized_keys      <-- Mode: 600 (-rw-------) Owned by <username>:<username>
```

```bash
# Correct Permission Command Sequence
chmod 700 /home/<username>/.ssh
chmod 600 /home/<username>/.ssh/authorized_keys
chown -R <username>:<username> /home/<username>/.ssh
```

---

## 🐛 Troubleshooting Windows PowerShell `ssh-keygen` Argument Bugs

### The Problem (`Too many arguments`)

When executing `ssh-keygen` in Windows PowerShell (v5.1) with empty passphrase arguments `-N ""`, PowerShell strips the empty quotes before passing arguments to `ssh-keygen.exe`.

PowerShell turns this command:
```powershell
# ❌ Fails in Windows PowerShell 5.1
ssh-keygen -t ed25519 -f $env:USERPROFILE\.ssh\id_ed25519_jenkins -N "" -C "ansible-deployment-key"
```

Into this truncated internal execution:
```
ssh-keygen.exe -t ed25519 -f C:\Users\Admin\.ssh\id_ed25519_jenkins -N -C ansible-deployment-key
```

`ssh-keygen` interprets `-C` as the argument to `-N` (setting the passphrase to `-C`), leaving `ansible-deployment-key` as an unexpected trailing argument, triggering:
```
Too many arguments.
usage: ssh-keygen [-q] ...
```

---

## ✅ Tested Solutions for PowerShell

### Solution 1: Interactive Execution (Recommended)

Omit `-N ""` and press **Enter** twice when prompted for a passphrase:

```powershell
ssh-keygen -t ed25519 -f $env:USERPROFILE\.ssh\id_ed25519_jenkins -C "ansible-deployment-key"
# Press Enter on "Enter passphrase"
# Press Enter on "Enter same passphrase again"
```

### Solution 2: Stop-Parsing Token (`--%`)

Use PowerShell's `--%` stop-parsing operator to pass raw argument strings without quote stripping:

```powershell
ssh-keygen --% -t ed25519 -f %USERPROFILE%\.ssh\id_ed25519_jenkins -N "" -C "ansible-deployment-key"
```

---

## 🔑 Key Identification & Comments

Always tag generated SSH keys with descriptive comments (`-C` flag) to maintain a clean audit log in `authorized_keys`:

| Key Type | Command | Resulting Comment in `authorized_keys` |
| :--- | :--- | :--- |
| **Admin Key** | `ssh-keygen -t ed25519 -C "abbenden-workstation"` | `ssh-ed25519 AAAAC3... abbenden-workstation` |
| **Jenkins Key** | `ssh-keygen -t ed25519 -C "ansible-deployment-key"` | `ssh-ed25519 AAAAC3... ansible-deployment-key` |
