# HoRus-Start — Proxmox VE IaC Infrastruktur-Plattform (v2.0-RC1)

🌐 **Sprachen**: [English](./README.md) | [Русский](./README.ru.md) | [Українська](./README.uk.md) | [日本語](./README.ja.md) | **Deutsch** | [Français](./README.fr.md)

---

## 🏛️ Übersicht & Konzept

**HoRus-Start v2** ist ein hochverfügbares Infrastructure-as-Code (IaC) Automatisierungs-Framework für das Bootstrapping und die Bereitstellung von Bare-Metal Proxmox VE Hypervisor-Clustern. Aufgebaut auf deklarativen Prinzipien, modularen Ansible-Rollen und einem versionierten JSON Runtime API v1 ermöglicht HoRus-Start ein durchgängiges Lifecycle-Management — von der Bare-Metal SSH-Konnektivität bis hin zu verteilten Speichersystemen und der Veröffentlichung von Cloud-Image-Katalogen.

> 🔒 **Architektur-Freeze Hinweis (v2.0-RC1)**: Die HoRus-Start Pipeline ist dauerhaft auf die **Stufen 0 bis 5** beschränkt. Die Pipeline endet nach dem Abschluss von Stage 5 (Asset Preparation & Validation). Manuelle Golden-Template-Erstellung, Terraform-Provisionierung und Anwendungs-Deployments erfolgen außerhalb von HoRus-Start.

---

## 🚀 Ausführungspipeline & Phasenarchitektur

HoRus-Start erzwingt eine deterministische 5-Stufen-Pipeline über alle aktiven Infrastrukturphasen:

```
[ Deklarative Konfiguration ] ──► 1. Discovery ──► 2. Normalisierung ──► 3. Planung ──► 4. Bereitstellung ──► 5. Verifizierung & Berichte
```

### Phasenübersicht

| Phase | Name | Beschreibung | Status |
| :--- | :--- | :--- | :--- |
| **Stage 0** | **Infrastructure Readiness Gate** | Preflight-Validierung, Formatierung von Zugangsdaten, Hardware-Auto-Discovery, Hash-Prüfung und Generierung von `stage0.json`. | **STABIL** |
| **Stage 1** | **Bootstrap Connectivity** | Prüft Erreichbarkeit der Knoten, generiert lokale ed25519 SSH-Schlüssel, verteilt öffentliche Schlüssel und verifiziert passwortlosen Root-SSH-Zugriff. | **STABIL** |
| **Stage 2** | **Base System Prep** | Konfiguriert APT-Repositorys (Debian 13 Trixie & pve-no-subscription), führt Kernel-Updates durch, installiert Systemwerkzeuge und optimiert sysctl. | **STABIL** |
| **Stage 3** | **Proxmox Cluster** | Initialisiert das `pvecm` Quorum-Cluster auf den Knoten und richtet corosync ein. | **STABIL** |
| **Stage 4** | **Storage Prepare** | Sichere Erkennung von Blockgeräten (`/dev/disk/by-id/`), Prüfung der System-OS-Sicherheit, Mount-Planung, Formatierung (ext4/ZFS) und PVE-Speicherregistrierung. | **STABIL** |
| **Stage 5** | **Asset Preparation & Validation** | Lädt Cloud-Images, ISO-Kataloge, VirtIO-Treiber und LXC-Caches herunter; veröffentlicht Assets in PVE-Speicher; prüft Hashes & `qemu-img`-Integrität. | **STABIL** |

> 🛑 **Pipeline-Ende**: Die Automatisierung endet nach Stage 5.

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
├── .github/                 # CI/CD Workflows (Secret Scanning, YAML Validation, Ansible-Lint)
├── config/                  # Deklarative Cluster- und Speicher-Konfigurationen
│   ├── examples/            # Beispiel-Konfigurationen für cluster, network, storage
│   ├── storage.yml
│   └── image_catalog.yml
├── credentials/             # SSH-Schlüssel und Passwörter (GIT-IGNORED)
├── docs/                    # Architektur-, Betriebs- und Sicherheitsdokumentation
│   ├── architecture/        # Domänenmodell, Planner-Spezifikation, Runtime API
│   ├── getting-started/     # Installation, Schnellstart, Anforderungen
│   ├── operations/          # Fehlerbehebung, Wiederherstellung, Backup
│   └── security/            # Sicherheitsmodell, Secrets Management, Threat Model
├── inventory/               # Ansible Inventar-Definitionen (hosts.yml)
├── playbooks/               # Haupt-Playbooks (00_*.yml bis 04_*.yml)
├── plugins/                 # Eigene Ansible Filter- und Action-Plugins
├── roles/                   # Modulare Rollen (storage_prepare, proxmox_templates etc.)
├── runtime/                 # Runtime API v1 Objekte (GIT-IGNORED)
├── schemas/                 # JSON Schemas zur Validierung
├── scripts/                 # Validierungs- und Prüfskripte
│   ├── stage0_preflight.py
│   ├── storage_validate.py
│   └── validate_schemas.py
├── horus-start              # Interaktiver CLI Launcher
├── SECURITY.md              # Sicherheitsrichtlinie & Schwachstellenmeldung
├── CONTRIBUTING.md          # Entwicklungsrichtlinien
├── CODE_OF_CONDUCT.md       # Verhaltenskodex der Community
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

# Stage 2: Basis-Systemvorbereitung (Debian 13)
ansible-playbook -i inventory/hosts.yml playbooks/01_base_system_prep.yml

# Stage 3: Proxmox Cluster-Einrichtung
ansible-playbook -i inventory/hosts.yml playbooks/02_proxmox_cluster.yml

# Stage 4: Speichervorbereitung (Testmodus / Dry-run)
ansible-playbook -i inventory/hosts.yml playbooks/03_storage_prepare.yml -e "storage_plan_only=true"

# Stage 4: Speichervorbereitung (Ausführung)
ansible-playbook -i inventory/hosts.yml playbooks/03_storage_prepare.yml

# Stage 5: Asset-Vorbereitung & Validierung
ansible-playbook -i inventory/hosts.yml playbooks/04_proxmox_templates.yml
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

Alle sensiblen Dateien wie private SSH-Schlüssel (`credentials/ssh/*`), Vault-Passwörter (`.vault_pass`), `.env`-Dateien und Ausführungsprotokolle sind strikt in `.gitignore` eingetragen. Automatische Secret-Scans (`ggshield`) laufen bei jedem Push.
