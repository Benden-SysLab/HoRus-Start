# ADR-0006: Unprivileged LXC Container Strategy & Feature Flags

## Status
**Accepted**

## Context
Privileged LXC containers map UID 0 inside the container directly to UID 0 on the Proxmox host, presenting a severe security vulnerability if a container breakout occurs. However, standard unprivileged LXC containers restrict systemd services, FUSE mounts, and process keyrings required by Docker, Vault, and systemd daemons.

## Decision
All LXC templates in HoRus-Start MUST be **Unprivileged** by default, configured with specific security feature flags:
- `nesting=1`: Enables systemd service management and nested container execution inside unprivileged LXC.
- `keyctl=1`: Enables Linux process keyring operations required by Docker, Vault, and PAM authentication.
- `fuse=1`: Enables FUSE filesystem mounts (e.g. SSHFS, Vault storage engines).

Privileged LXC containers are strictly prohibited unless explicitly authorized by architecture review.

## Consequences
### Positive
- Prevents host compromise in the event of an LXC container breach.
- Allows running systemd and container runtimes safely inside unprivileged LXC.

### Negative
- Some legacy kernel drivers or raw block device access remain restricted inside unprivileged containers.
