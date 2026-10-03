# Security

Please report vulnerabilities privately to the repository maintainers. Avoid posting credentials, private keys or full authentication logs in public issues.

Node passwords are entered during execution and are not stored in configuration files. The SSH private key belongs in an external directory such as `~/.ssh/horus/horus-pmx-node/`, never in Git. `runtime/` reports are local and ignored by Git. Review staged files before pushing:

```bash
git status --short
git diff --cached --check
git diff --cached --name-only
```

The GitHub secret scan workflow requires its GitGuardian secret to be configured in repository settings.
