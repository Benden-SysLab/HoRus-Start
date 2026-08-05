# Contributing to HoRus-Start

Thank you for your interest in contributing to **HoRus-Start**!

## Architectural Guidelines

HoRus-Start v2 operates under an **Architectural Freeze**. The core execution pipeline consists of Stages 0 through 5:

1. **Stage 0**: Infrastructure Readiness Gate
2. **Stage 1**: SSH Bootstrap
3. **Stage 2**: Debian 13 & Proxmox Repository Standardization
4. **Stage 3**: Cluster Formation
5. **Stage 4**: Storage Discovery & Provisioning
6. **Stage 5**: Asset Preparation & Validation

> ⚠️ **Note**: Do not add extra pipeline stages, automatic image modification tools, or post-bootstrap application deployments. Stages beyond Stage 5 (e.g. manual VM creation, Terraform, cloud-init) are explicitly external.

## Workflow & Development Rules

1. **Idempotency**: All playbooks and tasks must be completely idempotent. Re-running the pipeline multiple times must produce identical results without errors or state drift.
2. **Runtime API Compliance**: Any additions or modifications to reports must follow the **Runtime API v1** specification and pass `scripts/validate_schemas.py`.
3. **No Secrets**: Never commit secrets, passwords, tokens, or private keys.
4. **YAML Quality**: Ensure all YAML files pass `python scripts/validate_schemas.py` and `ansible-lint`.

## Submitting Pull Requests

1. Fork the repository and create your branch from `main`.
2. Make targeted changes keeping commits clear and focused.
3. Test your changes using `python3 scripts/validate_schemas.py`.
4. Open a Pull Request with a clear description of the problem solved.
