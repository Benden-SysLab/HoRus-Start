# 08 — OS Hardening & Security Specification

Security controls are pre-baked into the HoRus Golden Templates (VM ID 9000 and VM ID 9001) to ensure every deployed instance starts in an SRE-compliant, hardened posture.

---

## 🔒 1. Root Account & Password Hardening

- **Root Password Disabled**: The `root` account has no assigned password (`/etc/shadow` contains `!`), prohibiting direct password-based root logons.
- **Sudoers Restrictions**: Administrative actions must be executed via `sudo` under individual accounts (`abbenden-srv` or `jenkins-srv`), creating an auditable syslog trail.

```bash
# Verify root account status
sudo passwd -S root
# Expected output: root L ... (L = Locked)
```

---

## 🛡️ 2. OpenSSH Daemon Configuration (`/etc/ssh/sshd_config`)

Enforce hardened SSH defaults across all Golden Templates:

```ini
# /etc/ssh/sshd_config.d/50-horus-hardening.conf
PermitRootLogin prohibit-password
PasswordAuthentication no
PubkeyAuthentication yes
X11Forwarding no
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
```

Apply and verify:

```bash
sudo systemctl reload ssh
```

---

## ⚡ 3. Kernel Sysctl Hardening (`/etc/sysctl.d/99-horus-security.conf`)

Apply network stack hardening against IP spoofing, SYN flood attacks, and ICMP redirects:

```ini
# /etc/sysctl.d/99-horus-security.conf
# Disable IP packet forwarding (unless routing node)
net.ipv4.ip_forward = 0

# Protect against SYN flood attacks
net.ipv4.tcp_syncookies = 1

# Ignore ICMP broadcast requests
net.ipv4.icmp_echo_ignore_broadcasts = 1

# Disable ICMP redirect acceptance
net.ipv4.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0

# Log Martian packets (packets with impossible addresses)
net.ipv4.conf.all.log_martians = 1

# Enable Reverse Path Filtering (prevents IP spoofing)
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
```

Apply parameters:

```bash
sudo sysctl --system
```

---

## 🐋 4. Docker Socket Security & Group Isolation (Template 9001)

Access to the Docker UNIX socket (`/var/run/docker.sock`) is equivalent to root privileges.

To prevent privilege escalation attacks:
1. **Admin account (`abbenden-srv`) is NOT added to the `docker` group**. Administrative Docker management must be performed explicitly via `sudo -u docker-srv docker ...` or `sudo docker ...`.
2. **Service Account Isolation**: Only `docker-srv` and `jenkins-srv` hold membership in the `docker` group.

```bash
# Verify group memberships
grep docker /etc/group
# Expected output: docker:x:999:docker-srv,jenkins-srv
```
