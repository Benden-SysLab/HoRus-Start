# HoRus-Start

[English](README.md) · [Русский](README.ru.md) · [Українська](README.uk.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [日本語](README.ja.md)

Ansible-Projekt für die Ersteinrichtung von vier Proxmox-VE-Knoten und des Clusters **HoRus-SysLab**. Der aktive Ablauf richtet SSH, Debian/Proxmox-Paketquellen und Basispakete ein und prüft anschließend Cluster und Quorum. Getestet mit Debian 13 und Proxmox VE 9.2.21.

Knoten: `horus-pmx-node01` — `10.255.0.7`, `node02` — `10.255.0.8`, `node03` — `10.255.0.9`, `node04` — `10.255.0.10`.

## Ausführung unter WSL Debian

Python 3 und Ansible werden benötigt. Vorher `inventory/hosts.yml`, `config/network.yml` und `config/cluster.yml` prüfen.

```bash
export HORUS_SSH_KEY_DIR=/mnt/c/Users/Benden/.ssh/horus/horus-pmx-node
python3 scripts/stage0_preflight.py
ansible-playbook -i inventory/hosts.yml playbooks/00_bootstrap_connectivity.yml
ansible-playbook -i inventory/hosts.yml playbooks/01_base_system_prep.yml
ansible-playbook -i inventory/hosts.yml playbooks/02_proxmox_cluster.yml
```

Stage 0 erzeugt bei Bedarf den externen Ed25519-Schlüssel. Playbook 00 fragt Root-Passwörter im Terminal ab und richtet SSH ein. Playbook 01 konfiguriert Debian Trixie und Proxmox no-subscription und aktualisiert Pakete. Playbook 02 fügt Knoten nacheinander hinzu und prüft das Quorum. Bereits verbundene Knoten werden beim erneuten Ausführen übersprungen. Berichte liegen in `runtime/reports/` und werden von Git ignoriert.

Datenträger, GPUs, Proxmox-Speicher, VM-Vorlagen und Anwendungen werden separat eingerichtet. `./horus-start` startet Preflight und SSH; `playbooks/site.yml` startet die drei Ansible-Playbooks. Weitere Informationen: [Quickstart](docs/getting-started/QUICKSTART.md).
