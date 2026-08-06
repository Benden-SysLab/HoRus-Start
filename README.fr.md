# HoRus-Start — Plateforme IaC pour l'infrastructure Proxmox VE (v2.0-RC1)

🌐 **Langues**: [English](./README.md) | [Русский](./README.ru.md) | [Українська](./README.uk.md) | [日本語](./README.ja.md) | [Deutsch](./README.de.md) | **Français**

---

## 🏛️ Présentation et concept

**HoRus-Start v2** est un framework d'automatisation IaC (Infrastructure-as-Code) de niveau entreprise conçu pour le déploiement et la préparation de clusters d'hyperviseurs Proxmox VE bare-metal. Basé sur des principes déclaratifs, des rôles Ansible modulaires et une API Runtime JSON v1 versionnée, HoRus-Start offre une gestion complète du cycle de vie — de la connectivité SSH bare-metal jusqu'au stockage distribué et à la publication du catalogue d'images cloud.

> 🔒 **Avis de gel d'architecture (v2.0-RC1)**: Le pipeline HoRus-Start est définitivement limité aux **Étapes 0 à 5**. Le pipeline se termine après l'exécution de l'Étape 5 (Asset Preparation & Validation). La création manuelle de modèles Golden, le déploiement via Terraform et l'installation d'applications s'effectuent en dehors de HoRus-Start. Les instructions détaillées étape par étape pour la création manuelle des modèles Golden (VM ID 9000 Base, VM ID 9001 Docker, modèles LXC et standards SRE) sont documentées dans [docs/golden-images/](./docs/golden-images/).

---

## 🚀 Pipeline d'exécution et architecture des étapes

HoRus-Start applique un pipeline déterministe en 5 étapes pour toutes les phases d'infrastructure :

```
[ Configuration Déclarative ] ──► 1. Discovery ──► 2. Normalisation ──► 3. Planning ──► 4. Déploiement ──► 5. Vérification & Rapports
```

### Aperçu des étapes

| Étape | Nom | Description | Statut |
| :--- | :--- | :--- | :--- |
| **Stage 0** | **Infrastructure Readiness Gate** | Validation pré-vol, formatage des identifiants, auto-découverte du matériel, vérification des empreintes et émission de `stage0.json`. | **STABLE** |
| **Stage 1** | **Bootstrap Connectivity** | Vérifie l'accessibilité des nœuds, génère les clés SSH ed25519 locales, déploie les clés publiques et valide l'accès SSH root sans mot de passe. | **STABLE** |
| **Stage 2** | **Base System Prep** | Configure les dépôts APT (Debian 13 Trixie & pve-no-subscription), met à jour le noyau, installe les outils de base et ajuste sysctl. | **STABLE** |
| **Stage 3** | **Proxmox Cluster** | Initialise le cluster `pvecm` quorum sur les nœuds et configure le réseau corosync. | **STABLE** |
| **Stage 4** | **Storage Prepare** | Découverte sécurisée des disques physiques (`/dev/disk/by-id/`), vérification de la sécurité du disque système, planification, formatage ext4/ZFS et enregistrement des volumes PVE. | **STABLE** |
| **Stage 5** | **Asset Preparation & Validation** | Télécharge les images cloud, catalogues ISO, pilotes VirtIO et caches LXC ; publie les ressources sur le stockage PVE ; valide les empreintes et l'intégrité `qemu-img`. | **STABLE** |

> 🛑 **Fin du pipeline**: L'automatisation s'arrête définitivement après Stage 5.

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
├── .github/                 # Workflows CI/CD (analyse des secrets, validation YAML, ansible-lint)
├── config/                  # Configurations déclaratives du cluster et du stockage (SOT)
│   ├── examples/            # Exemples de configurations cluster, network, storage
│   ├── storage.yml
│   └── image_catalog.yml
├── credentials/             # Clés SSH et mots de passe (IGNORÉS DANS GIT)
├── docs/                    # Documentation d'architecture, d'exploitation et de sécurité
│   ├── architecture/        # Spécifications du modèle de domaine, du planificateur et de l'API Runtime
│   ├── getting-started/     # Installation, Démarrage rapide, Prérequis
│   ├── golden-images/       # Documentation complète des modèles Golden VM et LXC
│   ├── operations/          # Dépannage, Récupération, Sauvegarde & Restauration
│   └── security/            # Modèle de sécurité, Gestion des secrets, Modèle de menace
├── inventory/               # Définitions de l'inventaire Ansible (hosts.yml)
├── playbooks/               # Playbooks d'exécution principaux (00_*.yml à 04_*.yml)
├── plugins/                 # Plugins de filtres et d'actions Ansible personnalisés
├── roles/                   # Rôles modulaires (storage_prepare, proxmox_templates, etc.)
├── runtime/                 # Objets Runtime API v1 (IGNORÉS DANS GIT)
├── schemas/                 # Schémas JSON de validation
├── scripts/                 # Scripts de vérification et de validation
│   ├── stage0_preflight.py
│   ├── storage_validate.py
│   └── validate_schemas.py
├── horus-start              # Lanceur CLI interactif
├── SECURITY.md              # Politique de sécurité et signalement des vulnérabilités
├── CONTRIBUTING.md          # Guide de contribution
├── CODE_OF_CONDUCT.md       # Code de conduite de la communauté
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

# Stage 2: Préparation de base du système (Debian 13)
ansible-playbook -i inventory/hosts.yml playbooks/01_base_system_prep.yml

# Stage 3: Configuration du cluster Proxmox VE
ansible-playbook -i inventory/hosts.yml playbooks/02_proxmox_cluster.yml

# Stage 4: Préparation du stockage (Mode simulation / Dry-run)
ansible-playbook -i inventory/hosts.yml playbooks/03_storage_prepare.yml -e "storage_plan_only=true"

# Stage 4: Préparation du stockage (Exécution réelle)
ansible-playbook -i inventory/hosts.yml playbooks/03_storage_prepare.yml

# Stage 5: Préparation et validation des ressources
ansible-playbook -i inventory/hosts.yml playbooks/04_proxmox_templates.yml
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

Tous les fichiers sensibles, y compris les clés SSH privées (`credentials/ssh/*`), les mots de passe Vault (`.vault_pass`), les fichiers `.env` et les journaux d'exécution sont strictement ignorés via `.gitignore`. L'analyse automatique des secrets (`ggshield`) s'exécute à chaque push.
