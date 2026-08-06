# 20 — HoRus Infrastructure Standards Catalog

This catalog defines the mandatory baseline engineering standards enforced across all operating systems and containers built by the **HoRus Template Factory**.

---

## 🏛️ Baseline Standards Matrix

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HORUS INFRASTRUCTURE STANDARDS CATALOG                   │
└─────────────────────────────────────────────────────────────────────────────┘

  1. Filesystem Architecture Standard
     ├── Local Disks: VirtIO SCSI Single with Discard / TRIM enabled
     ├── Partitioning: Single root `/` partition (/dev/vda1 or /dev/sda1)
     └── Mount Options: `noatime,errors=remount-ro` for SSD/NVMe wear reduction

  2. Network Architecture Standard
     ├── Interface: VirtIO paravirtualized network driver (`eth0`)
     ├── IP Allocation: DHCP during Day-0/Day-1, static reservation via router
     └── DNS Resolver: Primary CoreDNS / Split-Horizon DNS (`10.10.0.1`)

  3. PKI & TLS Security Standard
     ├── Root CA: Internal Root CA trusted system-wide (`/usr/local/share/ca-certificates/`)
     └── SSL Protocols: Minimum TLS 1.2, preferred TLS 1.3 only

  4. Logging & Telemetry Standard
     ├── Local Retention: Systemd journal capped at 500 MiB or 7 days
     ├── Log Driver: Docker `json-file` limited to 10m x 3 files
     └── Telemetry Agent: Fluent Bit forwarding to central Loki/Elasticsearch

  5. Security Baseline Standard
     ├── SSH Access: Ed25519 public keys only, `PermitRootLogin no`
     ├── Firewall: UFW default deny incoming, port 22 allowed
     └── Root Account: Password disabled (`passwd -l root`)

  6. Container Runtime Standard
     ├── Runtime: Docker CE with `systemd` cgroup driver
     ├── Subnet Allocation: Default address pools `172.20.0.0/14`
     └── Socket Access: Isolated to `docker-srv` and `jenkins-srv`
```

---

## 📖 Deep Specification References

- **Filesystem & Disks**: [02-debian-9000-base.md](./02-debian-9000-base.md)
- **Docker & Container Runtime**: [03-debian-9001-docker.md](./03-debian-9001-docker.md)
- **LXC Container Architecture**: [04-lxc-templates.md](./04-lxc-templates.md)
- **Security & SSH Hardening**: [14-security-baseline.md](./14-security-baseline.md) & [ADR-0004](../adr/ADR-0004-ssh-key-authentication.md)
- **PKI & CA Certificates**: [15-pki.md](./15-pki.md) & [ADR-0005](../adr/ADR-0005-pki-trust-distribution.md)
