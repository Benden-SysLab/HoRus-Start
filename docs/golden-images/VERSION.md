# HoRus Golden Images Release History & Version Manifest

This document records the official version releases, package revisions, and architectural updates for the HoRus Golden Image catalog.

---

## 🚀 Current Release: v2026.08 (August 2026)

- **Release Date**: August 06, 2026
- **Architecture Freeze Version**: `v2.0-RC1`
- **Primary Tier-1 Distribution**: Debian 13 (Trixie)
- **Kernel Version**: `Linux 6.12.x-amd64`
- **Docker CE Version**: `27.x.x`
- **Fluent Bit Version**: `3.x.x`

### Release Highlights
- **Multi-OS Scope Expansion**: Standardized base specifications for Debian 13 (`9000`), Ubuntu 24.04 (`9010`), Rocky Linux 9 (`9020`), AlmaLinux 9 (`9030`), and Windows Server 2025 (`9090`).
- **Production Docker Daemon Configuration**: `/etc/docker/daemon.json` tuned with `json-file` log rotation (10m x 3), `cgroupdriver=systemd`, `live-restore`, `default-address-pools` (`172.20.0.0/14`), and disabled `userland-proxy`.
- **LXC Deep Feature Configuration**: Default unprivileged LXC templates (`9050`) with `nesting=1`, `keyctl=1`, and `fuse=1`.
- **Security Baseline**: Strict SSH key-only access (`PermitRootLogin no`, `PasswordAuthentication no`), passwordless sudo for `jenkins-srv`, and locked root account.
- **Embedded Internal PKI Trust**: `internal-ca.crt` injected into OS trust store for zero-trust HTTPS interactions across internal services.
