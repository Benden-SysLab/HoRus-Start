# HoRus-Start — Plateforme IaC pour l'infrastructure Proxmox VE

🌐 **Langues**: [English](./README.md) | [Русский](./README.ru.md) | [Українська](./README.uk.md) | [日本語](./README.ja.md) | [Deutsch](./README.de.md) | **Français**

---

## 🏛️ Présentation et concept

**HoRus-Start** est un framework d'automatisation IaC (Infrastructure-as-Code) de niveau entreprise conçu pour le déploiement, la préparation et la gestion de clusters d'hyperviseurs Proxmox VE bare-metal. Basé sur des principes déclaratifs, des rôles Ansible modulaires et une API Runtime JSON versionnée, HoRus-Start offre une gestion complète du cycle de vie — de la connectivité SSH bare-metal jusqu'au stockage distribué et aux modèles d'images cloud.

> 🔒 **Avis de gel d'architecture (Architecture Freeze)**: Les étapes 0 à 4 sont entièrement fonctionnelles, idempotentes et gelées dans le cadre du **Architecture Stabilization Milestone (Pre-Stage 5)**.

---

## 🚀 Pipeline d'exécution et architecture des étapes

HoRus-Start applique un pipeline déterministe en 5 étapes pour toutes les phases d'infrastructure :

```
[ Configuration Déclarative ] ──► 1. Discovery ──► 2. Normalisation ──► 3. Planning ──► 4. Déploiement ──► 5. Vérification & Rapports
```

### Aperçu des étapes

| Étape | Nom | Description | Statut |
| :--- | :--- | :--- | :--- |
| **Stage 0** | **Infrastructure Readiness Gate** | Validation pré-vol non destructive, génération automatique des modèles d'identifiants et de stockage, auto-découverte du matériel, vérification des empreintes d'artefacts et émission de `stage0.json`. | **STABLE** |
| **Stage 1** | **Bootstrap Connectivity** | Vérifie l'accessibilité des nœuds, génère les clés SSH ed25519, déploie les clés publiques et valide l'accès SSH root sans mot de passe. | **STABLE** |
| **Stage 2** | **Base System Prep** | Configure les dépôts APT (pve-no-subscription), effectue les mises à jour du noyau, installe les outils de base et ajuste sysctl. | **STABLE** |
| **Stage 3** | **Proxmox Cluster** | Initialise le cluster pvecm quorum sur les nœuds (`horus-pmx-node01` à `node04`) et configure le réseau corosync. | **STABLE** |
| **Stage 4** | **Storage Prepare** | Découverte sécurisée des disques physiques (`/dev/disk/by-id/`), vérification de la sécurité du disque système, planification, formatage ext4/ZFS et enregistrement des volumes PVE. | **STABLE** |
| **Stage 5** | **Golden Image Factory** | Téléchargement des images cloud (Ubuntu, Debian, Alpine) et création des modèles de VM Cloud-Init Proxmox. | *Étape suivante* |
| **Stage 6** | **Platform Bootstrap** | Infrastructure de gestion : création de terraform-srv, clés SSH, sudoers, jetons API et comptes de service. | *Planifié* |
| **Stage 7** | **Security** | Sécurisation du système : ajustements sysctl, configuration sshd, fail2ban, bannières motd, limites système. | *Planifié* |
| **Stage 8** | **Verification** | Auto-test complet de la plateforme (Cluster, Storage, Images, Templates, Users, SSH, Security, Reports). | *Planifié* |

---

## 💾 Architecture du framework de stockage (Stage 4)

Stage 4 fournit un moteur de réconciliation de stockage de niveau production :

1. **Discovery (Découverte)**: Analyser les périphériques via `lsblk -J` et associer les liens symboliques permanents `/dev/disk/by-id/` sans modifier l'état des disques.
2. **Sécurité du disque système**: Vérifie fermement qu'aucun stockage cible ne chevauche le disque système de l'OS (`/`, `/boot`, `/boot/efi`, `/etc/pve`).
3. **Planner (Planificateur)**: Calcule les différences exactes (`needs_format`, `needs_mkdir`, `needs_mount`, `needs_pvesm_add`) sauvegardées dans `runtime/plans/storage_plan.json`.
4. **Provisioning (Déploiement)**: Crée les unités de montage systemd, formate les systèmes de fichiers en respectant les règles de sécurité, met à jour `/etc/fstab` et enregistre les stockages dans Proxmox.
5. **Vérification**: Effectue un audit après déploiement, vérifie les montages via `findmnt`, détecte les dérives et génère `runtime/reports/stage4.json`.

---

## 📡 Runtime API v1 et Modèle de domaine

La communication entre les étapes dans HoRus-Start est régie par la **Runtime API v1**, éliminant les couplages cachés et les variables Ansible fragiles.

- **Config (`config/`)**: Source unique de vérité pour l'état désiré (Desired State).
- **Runtime (`runtime/`)**: Source unique de vérité pour l'état réel et planifié.
  - `runtime/discovery/` — Inventaire matériel découvert.
  - `runtime/facts/` — Faits d'infrastructure normalisés.
  - `runtime/plans/` — Plans d'exécution lisibles par machine.
  - `runtime/reports/` — Rapports de dérive et de fin d'étape.
  - `runtime/cache/`, `runtime/locks/`, `runtime/state/` — État interne privé.

Tous les objets JSON runtime publics respectent les schémas définis dans `schemas/runtime/` et contiennent les en-têtes obligatoires (`api_version: "v1"`, `schema_version: "1.0"`).

---

## 📁 Structure du dépôt

```
HoRus-Start/
├── config/                  # Configurations déclaratives du cluster et du stockage (SOT)
│   ├── storage.yml
│   └── storage_templates/
├── credentials/             # Clés SSH et mots de passe (IGNORÉS DANS GIT)
├── docs/                    # Documentation d'architecture
│   └── architecture/
│       ├── ARCHITECTURE_FREEZE.md
│       ├── DOMAIN_MODEL.md
│       ├── PLANNER_SPEC.md
│       └── RUNTIME_API_V1.md
├── inventory/               # Définitions de l'inventaire Ansible (hosts.yml)
├── playbooks/               # Playbooks d'exécution principaux (00_*.yml à 04_*.yml)
├── plugins/                 # Plugins de filtres et d'actions Ansible personnalisés
├── roles/                   # Rôles modulaires (storage_prepare, etc.)
├── runtime/                 # Objets Runtime API v1 (IGNORÉS DANS GIT)
│   ├── discovery/
│   ├── facts/
│   ├── plans/
│   └── reports/
├── schemas/                 # Schémas JSON de validation
├── scripts/                 # Scripts de vérification et de validation
│   ├── storage_validate.py
│   └── validate_schemas.py
├── horus-start              # Lanceur CLI interactif
└── README.md                # Documentation principale
```

---

## 🛠️ Utilisation et commandes

### 1. Lancer le script interactif
```bash
./horus-start
```

### 2. Exécuter les étapes individuelles
```bash
# Stage 0: Infrastructure Readiness Gate (Preflight Control Plane)
python3 scripts/stage0_preflight.py

# Stage 1: Connectivité SSH
ansible-playbook -i inventory/hosts.yml playbooks/00_bootstrap_connectivity.yml

# Stage 2: Préparation de base du système
ansible-playbook -i inventory/hosts.yml playbooks/01_base_system_prep.yml

# Stage 3: Configuration du cluster Proxmox VE
ansible-playbook -i inventory/hosts.yml playbooks/02_proxmox_cluster.yml

# Stage 4: Préparation du stockage (Mode simulation / Dry-run)
ansible-playbook -i inventory/hosts.yml playbooks/03_storage_prepare.yml -e "storage_plan_only=true"

# Stage 4: Préparation du stockage (Exécution réelle)
ansible-playbook -i inventory/hosts.yml playbooks/03_storage_prepare.yml
```

### 3. Exécuter les scripts de vérification
```bash
# Valider la configuration du stockage et l'inventaire des disques
python3 scripts/storage_validate.py

# Valider les schémas JSON de la Runtime API v1
python3 scripts/validate_schemas.py
```

---

## 🔒 Sécurité et confidentialité

Tous les fichiers sensibles, y compris les clés SSH privées (`credentials/ssh/*`), les mots de passe Vault (`.vault_pass`), les fichiers `.env` et les journaux temporaires sont strictement ignorés via `.gitignore`. Ne commitez jamais de secrets dans le contrôle de version.
