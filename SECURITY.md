# Security Policy

## Reporting Security Vulnerabilities

We take the security of **HoRus-Start** seriously. If you discover a security vulnerability, please **DO NOT** open a public issue on GitHub.

Instead, please report the issue privately:

- **Email**: `security@horus-start.org` (or contact the maintainers directly)
- Include details about the vulnerability, affected components, and steps to reproduce.

You will receive an initial response acknowledging your report within 48 hours.

## Security Architecture & Best Practices

HoRus-Start enforces strict credential and state isolation policies:

1. **No Credentials in Version Control**:
   - The `credentials/` directory is strictly ignored by `.gitignore` (except `.gitkeep` and `README.md`).
   - Cleartext passwords, SSH private keys, and API tokens are never tracked.

2. **Local SSH Keys & Identity Isolation**:
   - Ed25519 SSH keys are generated locally on the administrator control node during Stage 1.
   - Private keys never leave localhost or cross network boundaries in cleartext.

3. **Isolated Runtime State**:
   - All runtime execution logs, facts, and generated reports in `runtime/` are strictly ignored by version control.

4. **Automated Secret Scanning**:
   - GitGuardian (`ggshield`) and GitHub secret scanning workflows run on every push and pull request to detect accidental key leakage.

5. **Readiness Security Gate (Stage 0)**:
   - Stage 0 verifies credential format and alerts if default or empty passwords are detected before proceeding to execution.
