# 23 — Component Security Capability Matrix

This security matrix outlines access levels, execution privileges, authentication methods, TLS trust, audit logging, and firewall policies across all component archetypes in the **HoRus Template Factory**.

---

## 📊 Security Capability Matrix

| Component Archetype | Root Login | Password Auth | SSH Public Key | Passwordless Sudo | TLS CA Trust | Audit Logging | UFW Firewall | Docker Socket Access |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **VM Base (9000)** | ❌ Locked | ❌ Disabled | ✅ Ed25519 | ✅ `jenkins-srv` | ✅ Trusted | ✅ `auditd` | ✅ Port 22 Allowed | N/A |
| **VM Docker (9001)** | ❌ Locked | ❌ Disabled | ✅ Ed25519 | ✅ `jenkins-srv` | ✅ Trusted | ✅ `auditd` | ✅ Port 22 Allowed | ✅ `docker-srv` & `jenkins-srv` |
| **Unprivileged LXC (9050)**| ❌ Locked | ❌ Disabled | ✅ Ed25519 | ✅ `jenkins-srv` | ✅ Trusted | ✅ Journald | ✅ Port 22 Allowed | N/A |
| **Human Admin (`abbenden-srv`)**| N/A | ❌ Disabled | ✅ Ed25519 | ⚠️ Passworded | ✅ Trusted | ✅ Logged | N/A | ❌ Denied (`docker` group excluded) |
| **Automation (`jenkins-srv`)** | N/A | ❌ Disabled | ✅ Ed25519 | ✅ `NOPASSWD` | ✅ Trusted | ✅ Logged | N/A | ✅ Allowed (`docker` group) |
| **Runtime (`docker-srv`)** | N/A | ❌ Disabled | ❌ No Login | ❌ Denied | ✅ Trusted | ✅ Logged | N/A | ✅ Allowed (`docker` group) |

---

## 🔒 Security Enforcement Highlights

1. **Zero Password Footprint**: Password authentication over SSH is disabled globally across all templates.
2. **Strict Socket Boundary**: Human admins (`abbenden-srv`) cannot mount arbitrary root host volumes via the Docker socket because they are excluded from the `docker` group.
3. **Audited Privilege Elevation**: Automation actions performed by `jenkins-srv` via `sudo` are logged to system audit files and forwarded to central Loki telemetry by Fluent Bit.
