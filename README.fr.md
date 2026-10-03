# HoRus-Start

[English](README.md) · [Русский](README.ru.md) · [Українська](README.uk.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [日本語](README.ja.md)

Projet Ansible pour l'initialisation de quatre nœuds Proxmox VE et du cluster **HoRus-SysLab**. Le parcours actif prépare SSH, les dépôts Debian/Proxmox et les paquets de base, puis vérifie le cluster et son quorum. Testé avec Debian 13 et Proxmox VE 9.2.21.

Nœuds : `horus-pmx-node01` — `10.255.0.7`, `node02` — `10.255.0.8`, `node03` — `10.255.0.9`, `node04` — `10.255.0.10`.

## Exécution depuis WSL Debian

Python 3 et Ansible sont nécessaires. Vérifiez `inventory/hosts.yml`, `config/network.yml` et `config/cluster.yml` avant l'exécution.

```bash
export HORUS_SSH_KEY_DIR=/mnt/c/Users/Benden/.ssh/horus/horus-pmx-node
python3 scripts/stage0_preflight.py
ansible-playbook -i inventory/hosts.yml playbooks/00_bootstrap_connectivity.yml
ansible-playbook -i inventory/hosts.yml playbooks/01_base_system_prep.yml
ansible-playbook -i inventory/hosts.yml playbooks/02_proxmox_cluster.yml
```

Stage 0 crée une clé Ed25519 externe si nécessaire. Le playbook 00 demande les mots de passe root dans le terminal et prépare SSH. Le playbook 01 configure Debian Trixie et Proxmox no-subscription et met à jour les paquets. Le playbook 02 ajoute les nœuds un par un et vérifie le quorum. Une nouvelle exécution ignore les membres déjà présents. Les rapports locaux sont dans `runtime/reports/` et sont ignorés par Git.

Les disques, GPU, stockages Proxmox, modèles VM et applications sont configurés séparément. `./horus-start` lance le contrôle préalable et SSH ; `playbooks/site.yml` lance les trois playbooks Ansible. Voir le [guide rapide](docs/getting-started/QUICKSTART.md).
