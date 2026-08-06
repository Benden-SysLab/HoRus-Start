# 02 — Base Template Assembly & Multi-OS Standards (VM ID 9000 Range)

This guide provides step-by-step instructions for creating the primary **Base Template (VM ID 9000 Range)**, focusing on **Debian 13 (`debian-13-trixie-base`)**, alongside standard configurations for **Ubuntu 24.04 LTS**, **Rocky/AlmaLinux 9**, and **Windows Server**.

---

## 🎯 Base Template VM Allocation Table

| Distribution | Template VM ID | Name Convention | Default Package Manager |
| :--- | :--- | :--- | :--- |
| **Debian 13 (Trixie)** | `9000` | `debian-13-trixie-base` | `apt` |
| **Ubuntu 24.04 LTS** | `9010` | `ubuntu-2404-noble-base` | `apt` |
| **Rocky Linux 9** | `9020` | `rocky-9-minimal-base` | `dnf` |
| **AlmaLinux 9** | `9030` | `almalinux-9-minimal-base` | `dnf` |
| **Windows Server 2025**| `9090` | `win2025-std-base` | `winget` / `chocolatey` |

---

## Step 1: Create Virtual Machine Shell in Proxmox VE (ID 9000)

In Proxmox VE Web UI (or CLI), click **Create VM** and specify the exact parameters below:

- **General**:
  - Node: Select target cluster node (e.g., `node01`)
  - VM ID: `9000`
  - Name: `debian-13-trixie-base`
- **OS**:
  - ISO Image: Select `debian-testing-amd64-netinst.iso` (or official Debian 13 release ISO).
- **System**:
  - QEMU Agent: **Enable** (Check box active). *Crucial for Proxmox guest IP detection and graceful shutdown hooks.*
  - SCSI Controller: `VirtIO SCSI Single`
- **Disks**:
  - Storage: `storage-hdd` (or `storage-infra`)
  - Disk size: `10 GiB`
  - Bus/Device: `SCSI (scsi0)`
  - Discard: **Enable** (Required for `fstrim` and Thin Provisioning space reclamation)
- **CPU**:
  - Sockets: `1`, Cores: `1`
  - Type: `host` (Provides maximum CPU feature passthrough and performance)
- **Memory**:
  - Memory: `1024 MiB`
  - Ballooning: **Disable** (Fixed memory allocation prevents host memory fragmentation during template cloning)
- **Network**:
  - Bridge: `vmbr0`
  - Model: `VirtIO (paravirtualized)`

---

## Step 2: OS Installation via Netinst Console

1. Power on VM 9000 and open the **Console** tab.
2. Select **Install** (Text mode).
3. **Language / Location / Keyboard**: English / United States / American English.
4. **Network Configuration**: DHCP assigns an IP address.
5. **Hostname**: Enter `debian` (Scrubbed during sterilization).
6. **Root Password**: **LEAVE BLANK**.
   > 💡 **Architectural Note**: Leaving the root password blank automatically disables root password logins and grants passwordless `sudo` rights to the primary user created in the next step.
7. **Create User Account**:
   - Full name / Username: `abbenden-srv`
   - Password: Set a strong administrative password.
8. **Partitioning**: `Guided - use entire disk` ➔ `/dev/vda` ➔ `All files in one partition`.
9. **Software Selection**:
   - **UNCHECK ALL GRAPHICAL DESKTOPS**.
   - **CHECK ONLY**: `[*] SSH server` and `[*] standard system utilities`.
10. **GRUB Boot Loader**: Install to `/dev/vda`. Reboot upon completion.

---

## Step 3: Configure Passwordless SSH Access for Admin (`abbenden-srv`)

Log into the VM console as `abbenden-srv`.

### 1. Create `.ssh` Directory with Strict Security Permissions

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
touch ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys
```

### 2. Import Public SSH Key from Workstation

On your local workstation (PowerShell):

```powershell
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub | Set-Clipboard
```

In the VM console:

```bash
nano ~/.ssh/authorized_keys
# Paste key, save with Ctrl+O, Enter, Ctrl+X
```

---

## Step 4: Create Service Accounts (`jenkins-srv` & `docker-srv`)

Execute as `abbenden-srv` (via `sudo`):

### 1. Create `jenkins-srv` User for Ansible Automation

```bash
# Create user with home directory and bash shell
sudo useradd -m -s /bin/bash jenkins-srv
sudo passwd jenkins-srv

# Grant passwordless sudo privileges for Ansible playbook execution
echo "jenkins-srv ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/jenkins-srv
sudo chmod 0440 /etc/sudoers.d/jenkins-srv
```

### 2. Configure SSH Key for `jenkins-srv`

On your workstation (PowerShell), generate a dedicated key pair for Ansible/Jenkins:

```powershell
ssh-keygen -t ed25519 -f $env:USERPROFILE\.ssh\id_ed25519_jenkins -C "ansible-deployment-key"
Get-Content $env:USERPROFILE\.ssh\id_ed25519_jenkins.pub | Set-Clipboard
```

In the VM SSH session:

```bash
sudo mkdir -p /home/jenkins-srv/.ssh
sudo touch /home/jenkins-srv/.ssh/authorized_keys
sudo nano /home/jenkins-srv/.ssh/authorized_keys

sudo chmod 700 /home/jenkins-srv/.ssh
sudo chmod 600 /home/jenkins-srv/.ssh/authorized_keys
sudo chown -R jenkins-srv:jenkins-srv /home/jenkins-srv/.ssh
```

### 3. Create `docker-srv` Service Account (Unprivileged)

```bash
sudo useradd -m -s /bin/bash docker-srv
```

---

## Step 5: Install SRE Base Toolset & Fluent Bit Log Collector

```bash
# 1. Update system indices and upgrade existing packages
sudo apt update && sudo apt dist-upgrade -y

# 2. Install SRE Core Packages
sudo apt install -y qemu-guest-agent curl wget git vim btop dnsutils net-tools ufw rsync sudo gnupg2 gpgv unzip zip jq tree lsof iproute2

# 3. Add Official Fluent Bit GPG Key & Repository for Debian 13 (Trixie)
curl -fsSL https://packages.fluentbit.io/fluentbit.key | gpg --dearmor | sudo tee /usr/share/keyrings/fluentbit-keyring.gpg > /dev/null

echo "deb [signed-by=/usr/share/keyrings/fluentbit-keyring.gpg] https://packages.fluentbit.io/debian/trixie trixie main" | sudo tee /etc/apt/sources.list.d/fluent-bit.list

# 4. Install Fluent Bit and enable systemd service
sudo apt update && sudo apt install -y fluent-bit
sudo systemctl enable fluent-bit
sudo systemctl enable qemu-guest-agent
```

---

## 🌐 Enterprise Multi-OS Equivalents

### RHEL Variant (Rocky Linux 9 / AlmaLinux 9 — ID 9020 / 9030)
```bash
# Install SRE toolset on RHEL-based distributions
sudo dnf update -y
sudo dnf install -y qemu-guest-agent curl wget git vim btop bind-utils net-tools rsync sudo gnupg2 unzip zip jq tree lsof iproute
sudo systemctl enable qemu-guest-agent
```

### Windows Server Variant (Win2025 Standard — ID 9090)
```powershell
# Install VirtIO Drivers, QEMU Guest Agent & OpenSSH Server on Windows Server
Start-Service QEMU-GA
Set-Service QEMU-GA -StartupType Automatic
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service sshd -StartupType Automatic
```

---

## Step 6: SRE Sterilization & Template Freeze

Scrub unique instance identity before converting the VM into Template 9000:

```bash
# 1. Clean APT cache
sudo apt clean

# 2. Truncate system log files
sudo find /var/log -type f -exec truncate -s 0 {} \;

# 3. Reset Machine ID
sudo truncate -s 0 /etc/machine-id
sudo rm -f /var/lib/dbus/machine-id
sudo ln -s /etc/machine-id /var/lib/dbus/machine-id

# 4. Clear bash history and power down
history -c && history -w && sudo poweroff
```

In Proxmox VE Web UI: Right-click VM 9000 ➔ Click **Convert to Template**.
