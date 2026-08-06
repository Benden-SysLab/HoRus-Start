# ADR-0002: Docker Daemon Socket Security & User Isolation

## Status
**Accepted**

## Context
Adding administrative human users (`abbenden-srv`) to the `docker` group grants un-audited, root-equivalent access to the host filesystem, as any user in the `docker` group can mount `/` inside a container. Conversely, running containers as `root` without socket isolation introduces high privilege escalation risks.

## Decision
We enforce strict socket isolation and user account segregation:
1. The administrative human user (`abbenden-srv`) is **EXPLICITLY EXCLUDED** from the `docker` group.
2. A dedicated, unprivileged system user (`docker-srv`) is created and assigned to the `docker` group for running containerized workloads.
3. The automation user (`jenkins-srv`) is assigned to the `docker` group strictly to allow CI/CD pipelines to build and deploy containers.
4. The production `/etc/docker/daemon.json` configuration explicitly sets `"no-new-privileges": true` and enforces `systemd` cgroup drivers.

## Consequences
### Positive
- Prevents administrative human accounts from gaining un-audited root access via the Docker socket.
- Enforces least-privilege principles across container execution and build pipelines.

### Negative
- Human admins cannot directly run `docker ps` or `docker exec` without switching to `docker-srv` or using `sudo`.
