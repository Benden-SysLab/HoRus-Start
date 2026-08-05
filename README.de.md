# HoRus-Start — Proxmox VE IaC Infrastruktur-Plattform

🌐 **Sprachen**: [English](./README.md) | [Русский](./README.ru.md) | [Українська](./README.uk.md) | [日本語](./README.ja.md) | **Deutsch** | [Français](./README.fr.md)

---

## 🏛️ Übersicht & Konzept

**HoRus-Start** ist ein hochverfügbares Infrastructure-as-Code (IaC) Automatisierungs-Framework für das Bootstrapping, die Bereitstellung und die Verwaltung von Bare-Metal Proxmox VE Hypervisor-Clustern. Aufgebaut auf deklarativen Prinzipien, modularen Ansible-Rollen und einem versionierten JSON Runtime API ermöglicht HoRus-Start ein durchgängiges Lifecycle-Management — von der Bare-Metal SSH-Konnektivität bis hin zu verteilten Speichersystemen und Cloud-Image-Templates.

> 🔒 **Architektur-Freeze Hinweis (Architecture Freeze)**: Die Stufen 0 bis 4 sind voll funktionsfähig, idempotent und im Rahmen des **Architecture Stabilization Milestone (Pre-Stage 5)** eingefroren.

---

## 🚀 Ausführungspipeline & Phasenarchitektur

HoRus-Start erzwingt eine deterministische 5-Stufen-Pipeline über alle Infrastrukturphasen:

```
[ Deklarative Konfiguration ] ──► 1. Discovery ──► 2. Normalisierung ──► 3. Planung ──► 4. Bereitstellung ──► 5. Verifizierung & Berichte
```

### Phasenübersicht

| Phase | Name | Beschreibung | Status |
| :--- | :--- | :--- | :--- |
| **Stage 0** | **Infrastructure Readiness Gate** | Zerstörungsfreie Preflight-Validierung, automatische Vorlagenerstellung für Zugangsdaten und Speicher, Hardware-Auto-Discovery, Hash-Prüfung von Artefakten und Generierung von `stage0.json`. | **STABIL** |
| **Stage 1** | **Bootstrap Connectivity** | Prüft Erreichbarkeit der Knoten, generiert ed25519 SSH-Schlüssel, verteilt öffentliche Schlüssel und verifiziert passwortlosen Root-SSH-Zugriff. | **STABIL** |
| **Stage 2** | **Base System Prep** | Konfiguriert APT-Repositorys (pve-no-subscription), führt Kernel-Updates durch, installiert Systemwerkzeuge und optimiert sysctl. | **STABIL** |
| **Stage 3** | **Proxmox Cluster** | Initialisiert das pvecm Quorum-Cluster auf den Knoten (`horus-pmx-node01` bis `node04`) und richtet corosync ein. | **STABIL** |
| **Stage 4** | **Storage Prepare** | Sichere Erkennung von Blockgeräten (`/dev/disk/by-id/`), Prüfung der System-OS-Sicherheit, Mount-Planung, Formatierung (ext4/ZFS) und PVE-Speicherregistrierung. | **STABIL** |
| **Stage 5** | **Golden Image Factory** | Lädt Cloud-OS-Images (Ubuntu, Debian, Alpine) herunter und erstellt Proxmox Cloud-Init VM-Templates. | *Nächste Phase* |
| **Stage 6** | **Platform Bootstrap** | Management-Infrastruktur-Bereitstellung: terraform-srv, SSH-Schlüssel, Sudoers, API-Token, Service-Accounts. | *Geplant* |
| **Stage 7** | **Security** | Systemhärtung: sysctl-Tuning, sshd-Konfiguration, fail2ban, motd-Banner, Systemgrenzen (limits). | *Geplant* |
| **Stage 8** | **Verification** | Vollständiger Plattform-Self-Test (Cluster, Storage, Images, Templates, Users, SSH, Security, Reports). | *Geplant* |

---

## 💾 Stage 4 Speicher-Framework Architecture

Stage 4 bietet eine produktionsreife Engine zur Speicher-Abgleichung:

1. **Discovery**: Scannt Geräte über `lsblk -J` und verknüpft sie mit dauerhaften `/dev/disk/by-id/` Symlinks, ohne den Festplattenstatus zu verändern.
2. **OS-Sicherheitssperre**: Stellt sicher, dass Zielspeicher nicht mit der System-Festplatte des Betriebssystems (`/`, `/boot`, `/boot/efi`, `/etc/pve`) kollidieren.
3. **Planner**: Berechnet genaue Differenzen (`needs_format`, `needs_mkdir`, `needs_mount`, `needs_pvesm_add`) und speichert diese in `runtime/plans/storage_plan.json`.
4. **Provisioning**: Erstellt systemd Mount-Units, formatiert Dateisysteme unter Einhaltung von Sicherheitsprüfungen, aktualisiert `/etc/fstab` und registriert Speicher in Proxmox.
5. **Verifizierung**: Führt Audits nach der Bereitstellung durch, prüft aktive Mounts via `findmnt`, erkennt Drift und generiert `runtime/reports/stage4.json`.

---

## 📡 Runtime API v1 & Domänenmodell

Die phasenübergreifende Kommunikation in HoRus-Start wird über die **Runtime API v1** geregelt, was verdeckte Abhängigkeiten und fragile Ansible-Variablen eliminiert.

- **Config (`config/`)**: Einzige Quelle der Wahrheit für den Soll-Zustand (Desired State).
- **Runtime (`runtime/`)**: Einzige Quelle der Wahrheit für den Ist- und Plan-Zustand.
  - `runtime/discovery/` — Erfasste Hardware-Inventare.
  - `runtime/facts/` — Normalisierte Infrastruktur-Fakten.
  - `runtime/plans/` — Maschinenlesbare Ausführungspläne.
  - `runtime/reports/` — Drift-Analysen und Ausführungsberichte.
  - `runtime/cache/`, `runtime/locks/`, `runtime/state/` — Interner Zustand.

Alle öffentlichen Runtime JSON-Objekte entsprechen den Schemas in `schemas/runtime/` und enthalten standardisierte Header (`api_version: "v1"`, `schema_version: "1.0"`).

---

## 📁 Repository-Struktur

```
HoRus-Start/
├── config/                  # Deklarative Cluster- und Speicher-Konfigurationen (SOT)
│   ├── storage.yml
│   └── storage_templates/
├── credentials/             # SSH-Schlüssel und Passwörter (GIT-IGNORED)
├── docs/                    # Architektur-Dokumentation
│   └── architecture/
│       ├── ARCHITECTURE_FREEZE.md
│       ├── DOMAIN_MODEL.md
│       ├── PLANNER_SPEC.md
│       └── RUNTIME_API_V1.md
├── inventory/               # Ansible Inventar-Definitionen (hosts.yml)
├── playbooks/               # Haupt-Playbooks (00_*.yml bis 04_*.yml)
├── plugins/                 # Eigene Ansible Filter- und Action-Plugins
├── roles/                   # Modulare Rollen (storage_prepare, etc.)
├── runtime/                 # Runtime API v1 Objekte (GIT-IGNORED)
│   ├── discovery/
│   ├── facts/
│   ├── plans/
│   └── reports/
├── schemas/                 # JSON Schemas zur Validierung
├── scripts/                 # Validierungs- und Prüfskripte
│   ├── storage_validate.py
│   └── validate_schemas.py
├── horus-start              # Interaktiver CLI Launcher
└── README.md                # Hauptdokumentation
```

---

## 🛠️ Benutzung & Ausführung

### 1. Interaktiven Launcher starten
```bash
./horus-start
```

### 2. Einzelne Phasen ausführen
```bash
# Stage 0: Infrastructure Readiness Gate (Preflight Control Plane)
python3 scripts/stage0_preflight.py

# Stage 1: SSH-Konnektivität
ansible-playbook -i inventory/hosts.yml playbooks/00_bootstrap_connectivity.yml

# Stage 2: Basis-Systemvorbereitung
ansible-playbook -i inventory/hosts.yml playbooks/01_base_system_prep.yml

# Stage 3: Proxmox Cluster-Einrichtung
ansible-playbook -i inventory/hosts.yml playbooks/02_proxmox_cluster.yml

# Stage 4: Speichervorbereitung (Testmodus / Dry-run)
ansible-playbook -i inventory/hosts.yml playbooks/03_storage_prepare.yml -e "storage_plan_only=true"

# Stage 4: Speichervorbereitung (Ausführung)
ansible-playbook -i inventory/hosts.yml playbooks/03_storage_prepare.yml
```

### 3. Validierungsskripte ausführen
```bash
# Speicher-Konfiguration & Inventar prüfen
python3 scripts/storage_validate.py

# Runtime API v1 JSON Schemas prüfen
python3 scripts/validate_schemas.py
```

---

## 🔒 Sicherheit & Datenschutz

Alle sensiblen Dateien wie private SSH-Schlüssel (`credentials/ssh/*`), Vault-Passwörter (`.vault_pass`), `.env`-Dateien und temporäre Ausführungsprotokolle sind strikt in `.gitignore` eingetragen. Übertragen Sie niemals Zugangsdaten in die Versionskontrolle.
