# 10 — Known Issues & Troubleshooting Log

This document records historical problems encountered during template preparation, root cause analyses, and battle-tested solutions.

---

## 📋 Problem Registry & Solutions

### Issue 1: `useradd` / `usermod` Failure (`process is currently used`)
- **Symptom**: Attempting to rename an existing user (e.g. `abbenden` to `abbenden-srv`) fails with error `usermod: user abbenden is currently used by process 1234`.
- **Root Cause**: Active SSH session or background systemd user daemon owned by the target user locks the account process.
- **Resolution**: Create the correct user name (`abbenden-srv`) **directly during Debian OS netinst installation**, avoiding post-install account renaming.

---

### Issue 2: `Permission denied (publickey)` on SSH Connection
- **Symptom**: Public key authentication fails even though the key was added to `authorized_keys`.
- **Root Cause**: Overly permissive file mode on `.ssh` directory or `authorized_keys` file, OR incorrect ownership (e.g., owned by `root:root` instead of `jenkins-srv:jenkins-srv`).
- **Resolution**: Re-apply strict ownership and permissions:
  ```bash
  sudo chown -R jenkins-srv:jenkins-srv /home/jenkins-srv/.ssh
  sudo chmod 700 /home/jenkins-srv/.ssh
  sudo chmod 600 /home/jenkins-srv/.ssh/authorized_keys
  ```

---

### Issue 3: Fluent Bit Repository Key Verification Failure on Debian 13 (`gpgv` / `sqv` error)
- **Symptom**: `apt update` fails when adding Fluent Bit repository on Debian 13 (Trixie) with GPG signature validation error (`Missing key... verify signature`).
- **Root Cause**: Minimal Debian 13 installations lack `gnupg2` and use new APT key validation requirements (`/usr/share/keyrings/`).
- **Resolution**: Explicitly install `gnupg2` and `gpgv`, dearmor the key into `/usr/share/keyrings/fluentbit-keyring.gpg`, and use `[signed-by=...]` in `sources.list.d`:
  ```bash
  sudo apt install -y gnupg2 gpgv
  curl -fsSL https://packages.fluentbit.io/fluentbit.key | gpg --dearmor | sudo tee /usr/share/keyrings/fluentbit-keyring.gpg > /dev/null
  echo "deb [signed-by=/usr/share/keyrings/fluentbit-keyring.gpg] https://packages.fluentbit.io/debian/trixie trixie main" | sudo tee /etc/apt/sources.list.d/fluent-bit.list
  ```

---

### Issue 4: Docker Pull Timeout (`net/http: TLS handshake timeout`)
- **Symptom**: `docker run hello-world` fails with `net/http: TLS handshake timeout` when downloading images from Docker Hub.
- **Root Cause**: Network filtering or DPI blocks direct access to `registry.docker.io`.
- **Resolution**: Configure container registry mirrors in `/etc/docker/daemon.json` or route Docker daemon traffic through an outbound proxy service:
  ```json
  {
    "registry-mirrors": [
      "https://mirror.gcr.io"
    ]
  }
  ```

---

### Issue 5: PowerShell `ssh-keygen` `Too many arguments` Error
- **Symptom**: Running `ssh-keygen` with `-N ""` in Windows PowerShell outputs `Too many arguments`.
- **Root Cause**: PowerShell 5.1 strips empty string arguments `-N ""`, causing `-C` to be consumed as the passphrase value and leaving trailing unparsed arguments.
- **Resolution**: Omit `-N ""` and press Enter twice interactively, or use PowerShell stop-parsing syntax: `ssh-keygen --% -t ed25519 -f %USERPROFILE%\.ssh\id_ed25519_jenkins -N "" -C "ansible-deployment-key"`.
