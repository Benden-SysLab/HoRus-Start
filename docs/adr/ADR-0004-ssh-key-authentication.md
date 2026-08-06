# ADR-0004: Strict Ed25519 SSH Key-Only Authentication & Locked Root

## Status
**Accepted**

## Context
Standard password authentication and remote `root` SSH logins are major targets for brute-force attacks and security compromise.

## Decision
All HoRus templates enforce strict SSH key-only authentication:
1. `PermitRootLogin no` and `PasswordAuthentication no` are enforced in `/etc/ssh/sshd_config.d/99-horus-hardening.conf`.
2. The `root` account password is locked (`passwd -l root`).
3. Access is granted exclusively via high-security Ed25519 SSH public keys imported into `~/.ssh/authorized_keys` for `abbenden-srv` (human admin) and `jenkins-srv` (automation).
4. `jenkins-srv` is granted passwordless `sudo` rights (`NOPASSWD: ALL`).

## Consequences
### Positive
- Completely eliminates password brute-force attack vectors over SSH.
- Enforces auditable identity delegation via distinct SSH key pairs.

### Negative
- Administrators must possess their authorized Ed25519 private key to gain SSH access.
