# 06 — Jenkins & Ansible Automation Access Setup

To enable seamless, unattended infrastructure orchestration via Ansible and Jenkins CI/CD, a dedicated, privileged service account named `jenkins-srv` is baked directly into the Golden Templates.

---

## 👤 `jenkins-srv` Account Specification

```
User Name:        jenkins-srv
Primary Group:    jenkins-srv
Secondary Groups: docker (on Template 9001)
Home Directory:   /home/jenkins-srv
Default Shell:    /bin/bash
Sudo Privileges:  NOPASSWD: ALL (via /etc/sudoers.d/jenkins-srv)
SSH Auth:         Ed25519 Public Key Only
```

---

## 🔑 Dedicated SSH Key Generation & Comment Standard

> 💡 **Best Practice**: The automation SSH key pair **MUST** be separate from human administrator SSH keys. It must be generated without a passphrase (`-N ""`) to allow headless background execution by Ansible/Jenkins controllers, and include a clear functional comment (`-C "ansible-deployment-key"`).

### 1. Generating Key Pair on Workstation

**Windows PowerShell**:
```powershell
ssh-keygen -t ed25519 -f $env:USERPROFILE\.ssh\id_ed25519_jenkins -C "ansible-deployment-key"
```

**Linux / macOS Terminal**:
```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_jenkins -C "ansible-deployment-key"
```

This creates two files:
- `id_ed25519_jenkins` (Private key — keep secure on controller node or Jenkins credentials store)
- `id_ed25519_jenkins.pub` (Public key — baked into `authorized_keys` of Template 9000 and 9001)

---

## 📝 Step-by-Step Configuration Commands (On Template OS)

Execute these commands inside the target VM before converting it into a template:

```bash
# 1. Create service user with home directory and bash shell
sudo useradd -m -s /bin/bash jenkins-srv

# 2. Set user password
sudo passwd jenkins-srv

# 3. Configure passwordless sudo privileges
echo "jenkins-srv ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/jenkins-srv
sudo chmod 0440 /etc/sudoers.d/jenkins-srv

# 4. Create .ssh directory and authorized_keys file
sudo mkdir -p /home/jenkins-srv/.ssh
sudo touch /home/jenkins-srv/.ssh/authorized_keys

# 5. Populate authorized_keys with id_ed25519_jenkins.pub content
sudo nano /home/jenkins-srv/.ssh/authorized_keys

# 6. Apply strict SSH ownership and permissions
sudo chmod 700 /home/jenkins-srv/.ssh
sudo chmod 600 /home/jenkins-srv/.ssh/authorized_keys
sudo chown -R jenkins-srv:jenkins-srv /home/jenkins-srv/.ssh
```

---

## 🧪 Verifying Automation Access

From your administrator workstation or Jenkins runner:

```bash
# Test passwordless SSH connectivity
ssh -i ~/.ssh/id_ed25519_jenkins jenkins-srv@<VM_IP_ADDRESS> "hostname && whoami"
# Expected output:
# <hostname>
# jenkins-srv

# Test passwordless sudo execution
ssh -i ~/.ssh/id_ed25519_jenkins jenkins-srv@<VM_IP_ADDRESS> "sudo id"
# Expected output:
# uid=0(root) gid=0(root) groups=0(root)
```
