# 14 — Security Posture & Hardening Baseline

Every HoRus Golden Image enforces a strict security posture prior to being converted into a template. This document details the mandatory security parameters applied across system access, network protocols, firewalling, and audit logging.

---

## 🔒 Mandatory SSH Daemon Hardening (`/etc/ssh/sshd_config.d/99-horus-hardening.conf`)

All Linux Golden Templates enforce the following `/etc/ssh/sshd_config` parameters:

```ini
# HoRus Security Baseline - SSH Hardening
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
X11Forwarding no
AllowTcpForwarding no
ClientAliveInterval 300
ClientAliveCountMax 2
MaxAuthTries 3
KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org,diffie-hellman-group16-sha512
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.org
MACs hmac-sha2-512-etm@openssh.com
```

### Security Rationale Matrix

| Parameter | Value | Security Objective |
| :--- | :--- | :--- |
| **`PermitRootLogin`** | `no` | Prevents direct SSH access as `root`. Forces all administrative access through passwordless SSH keys to `abbenden-srv` or `jenkins-srv`. |
| **`PasswordAuthentication`** | `no` | Completely eliminates SSH password brute-force vectors. Only authorized Ed25519 SSH keys are accepted. |
| **`X11Forwarding`** | `no` | Disables X11 graphical display redirection over SSH tunnels, preventing X11 session hijacking. |
| **`AllowTcpForwarding`** | `no` | Prevents unauthorized SSH port forwarding and socks proxying through the instance. |
| **`ClientAliveInterval`** | `300` | Automatically drops idle SSH connections after 5 minutes of inactivity. |

---

## 🛡️ Host Firewall & Intrusion Prevention

### 1. UFW Default Egress/Ingress Policy
```bash
# Set strict default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH management port
sudo ufw allow 22/tcp comment 'Allow SSH Management'
sudo ufw enable
```

### 2. Auditd & Journald Security Logging
- System audit daemon (`auditd`) logs user privilege elevations (`sudo`), file permission modifications (`/etc/passwd`, `/etc/sudoers`), and failed authentication attempts.
- Systemd journald logs are persisted and monitored by Fluent Bit for real-time log shipping.
