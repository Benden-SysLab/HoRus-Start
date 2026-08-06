# ADR-0005: Embedded Infrastructure Root CA Trust Distribution

## Status
**Accepted**

## Context
In enterprise private cloud environments, internal services (HashiCorp Vault, Harbor Registry, Gitea, Jenkins) communicate over TLS using certificates issued by an internal Root CA. If cloned instances do not trust the Root CA, system tools (`curl`, `git`, `docker`, `apt`) fail with SSL verification errors, prompting developers to use insecure flags like `curl -k`.

## Decision
The internal Infrastructure Root CA certificate (`internal-ca.crt`) is embedded directly into the operating system trust store (`/usr/local/share/ca-certificates/`) during template pre-baking, followed by running `update-ca-certificates`.

## Consequences
### Positive
- All cloned instances automatically trust internal HTTPS endpoints out of the box.
- Completely eliminates the need for insecure `-k` / `--insecure` flags in automation scripts.

### Negative
- CA certificate rotation requires updating the template or pushing updated certificates via Ansible across running instances.
