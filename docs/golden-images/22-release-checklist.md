# 22 — Template Readiness Release Checklist

Before marking any candidate Virtual Machine or LXC Container as **"Template Ready"** in Proxmox VE, the build engineer or automated pipeline MUST verify every item in this release checklist.

---

## 📋 Interactive Readiness Release Checklist

### 1. Operating System & SRE Toolset
- [ ] Operating system packages updated (`apt update && apt dist-upgrade -y` or `dnf update -y`).
- [ ] QEMU Guest Agent installed and active (`systemctl is-active qemu-guest-agent`).
- [ ] SRE Core Toolset present (`curl`, `wget`, `git`, `vim`, `btop`, `dnsutils`, `iproute2`, `rsync`, `sudo`, `gnupg2`, `unzip`, `zip`, `jq`, `tree`, `lsof`).
- [ ] Fluent Bit log forwarder installed and enabled (`systemctl is-enabled fluent-bit`).

### 2. User Accounts & Privilege Management
- [ ] Root password account locked (`passwd -S root` shows `L` or `!`).
- [ ] Administrative account `abbenden-srv` exists with valid Ed25519 public SSH key.
- [ ] Automation account `jenkins-srv` exists with valid Ed25519 public SSH key.
- [ ] `jenkins-srv` granted passwordless sudo privileges (`/etc/sudoers.d/jenkins-srv` verified).
- [ ] Unprivileged service user `docker-srv` created (for Docker templates).

### 3. Security & SSH Hardening
- [ ] SSH password authentication explicitly disabled (`PasswordAuthentication no`).
- [ ] Remote root SSH login disabled (`PermitRootLogin no`).
- [ ] SSH host keys preserved or marked for regeneration upon first clone boot.
- [ ] Host firewall active (`ufw status` allows port 22/tcp).
- [ ] Internal Root CA certificate installed and trusted (`/usr/local/share/ca-certificates/internal-ca.crt`).

### 4. Container Runtime (Template ID 9001 Docker)
- [ ] Docker CE installed and active (`systemctl is-active docker`).
- [ ] Production `/etc/docker/daemon.json` present (`json-file` max-size 10m x 3, `systemd` cgroup, `live-restore`).
- [ ] Service user `docker-srv` and `jenkins-srv` added to `docker` group.
- [ ] Admin user `abbenden-srv` **EXPLICITLY EXCLUDED** from `docker` group.

### 5. SRE Sterilization & Machine Scrubbing
- [ ] APT / DNF package manager cache cleared (`apt clean`).
- [ ] All log files in `/var/log` truncated to 0 bytes.
- [ ] Machine ID scrubbed (`truncate -s 0 /etc/machine-id` and dbus machine-id symlinked).
- [ ] Bash and shell history erased (`history -c && history -w`).
- [ ] Temporary files in `/tmp` and `/var/tmp` deleted.

### 6. Validation & Freeze
- [ ] Virtual Machine powered down gracefully (`poweroff`).
- [ ] Candidate VM converted to Proxmox Template (`qm template <vmid>`).
- [ ] Version tag applied (`debian-13-trixie-base-v2026.08`).
- [ ] Test clone instantiated and verified via Ansible ping.
