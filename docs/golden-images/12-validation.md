# 12 — Template Validation & Pre-Freeze Audit Checklist

Before converting any candidate Virtual Machine or LXC Container into an official **HoRus Golden Template**, it must pass 100% of the verification checks in this audit checklist.

---

## 📋 Comprehensive Pre-Freeze Audit Checklist

Execute these verification commands on the candidate instance prior to sterilization:

```
+---------------------------------------------------------------------------------------+
|                             GOLDEN TEMPLATE VALIDATION MATRIX                         |
+----+-----------------------+---------------------------------------+------------------+
| #  | Component / Subsystem | Verification Command / Procedure      | Expected Status  |
+----+-----------------------+---------------------------------------+------------------+
| 01 | QEMU Guest Agent      | `systemctl status qemu-guest-agent`   | Active (running) |
| 02 | SSH Daemon            | `systemctl status ssh`                | Active (running) |
| 03 | Admin SSH Login       | `ssh -i id_ed25519 abbenden-srv@ip`   | Passwordless     |
| 04 | Jenkins SSH Login     | `ssh -i id_ed25519_jenkins jenkins@ip`| Passwordless     |
| 05 | Jenkins Sudo Rights   | `sudo -u jenkins-srv sudo id`         | uid=0(root)      |
| 06 | Root Password Status  | `sudo passwd -S root`                 | Locked (L / !)   |
| 07 | Root SSH Login        | `ssh root@ip`                         | Rejected         |
| 08 | PKI Certificate Trust | `curl -I https://internal-ca-test/`   | HTTP 200 / SSL OK|
| 09 | DNS Resolution        | `dig +short google.com`               | IP Resolved      |
| 10 | Internet Egress       | `curl -I https://debian.org`          | HTTP 200 OK      |
| 11 | Package Manager       | `sudo apt update`                     | No GPG Errors    |
| 12 | Docker Execution      | `sudo -u docker-srv docker run hello` | Success (ID 9001)|
| 13 | Fluent Bit Service    | `systemctl is-enabled fluent-bit`     | Enabled          |
| 14 | Machine ID Reset      | `cat /etc/machine-id`                 | Empty / 0 bytes  |
| 15 | System Log Truncation | `du -sh /var/log`                     | < 1 MiB          |
| 16 | History Scrubbing     | `history`                             | Empty            |
+----+-----------------------+---------------------------------------+------------------+
```

---

## 🧪 Detailed Verification Commands

### 1. Verify QEMU Guest Agent Integration
```bash
sudo systemctl is-active qemu-guest-agent
# Output: active
```

### 2. Verify Root Account Lock & Sudo Privileges
```bash
sudo passwd -S root
# Output: root L ... (Locked)

sudo -u jenkins-srv sudo id
# Output: uid=0(root) gid=0(root) groups=0(root)
```

### 3. Verify PKI CA Certificate Trust
```bash
openssl verify /usr/local/share/ca-certificates/internal-ca.crt
# Output: /usr/local/share/ca-certificates/internal-ca.crt: OK
```

### 4. Verify Docker Socket Security (Template 9001)
```bash
# Verify docker-srv execution succeeds
sudo -u docker-srv docker run --rm hello-world

# Verify admin abbenden-srv is NOT in docker group
groups abbenden-srv | grep -v docker
```

### 5. Verify Machine ID Reset State
```bash
ls -l /etc/machine-id
# Output: -rw-r--r-- 1 root root 0 ... /etc/machine-id (0 bytes)
```
