# Secrets and SSH keys

Node root passwords are requested interactively for SSH bootstrap. The master root password is requested only when a worker needs to join the Proxmox cluster. These values remain in Ansible process memory for that run; they are not committed to Git.

The Ed25519 private key is stored outside the repository in `~/.ssh/horus/horus-pmx-node/` by default. In WSL, set `HORUS_SSH_KEY_DIR=/mnt/c/Users/Benden/.ssh/horus/horus-pmx-node` to use the Windows key directory. Stage 0 creates the key pair if both files are absent. The default filename is `horus-pmx-cluster`; `HORUS_SSH_KEY_NAME` overrides it.

The `runtime/` directory and common key, token and environment-file patterns are ignored by Git. Before pushing, inspect `git diff --cached` and `git status --short` for accidental secrets. Never paste passwords into issues, logs or chat messages.
