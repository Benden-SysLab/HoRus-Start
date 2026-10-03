# HoRus-Start

[English](README.md) · [Русский](README.ru.md) · [Українська](README.uk.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [日本語](README.ja.md)

Ansible-проєкт для початкового налаштування чотирьох вузлів Proxmox VE та створення кластера **HoRus-SysLab**. Робочі етапи налаштовують SSH, репозиторії Debian/Proxmox, базові пакети й перевіряють кластер. Перевірено на Debian 13 та Proxmox VE 9.2.21.

Вузли: `horus-pmx-node01` — `10.255.0.7`, `node02` — `10.255.0.8`, `node03` — `10.255.0.9`, `node04` — `10.255.0.10`.

## Запуск із WSL Debian

Потрібні Python 3 та Ansible. Перевірте `inventory/hosts.yml`, `config/network.yml` та `config/cluster.yml` перед запуском.

```bash
export HORUS_SSH_KEY_DIR=/mnt/c/Users/Benden/.ssh/horus/horus-pmx-node
python3 scripts/stage0_preflight.py
ansible-playbook -i inventory/hosts.yml playbooks/00_bootstrap_connectivity.yml
ansible-playbook -i inventory/hosts.yml playbooks/01_base_system_prep.yml
ansible-playbook -i inventory/hosts.yml playbooks/02_proxmox_cluster.yml
```

Stage 0 створює зовнішній ключ Ed25519 за потреби. Playbook 00 запитує паролі root у терміналі та налаштовує SSH. Playbook 01 налаштовує Debian Trixie і Proxmox no-subscription та оновлює пакети. Playbook 02 послідовно додає вузли і перевіряє quorum. Повторний запуск пропускає вже додані вузли. Звіти містяться в `runtime/reports/` і не потрапляють до Git.

Диски, GPU, сховища, шаблони VM та застосунки налаштовуються окремо. `./horus-start` виконує preflight і SSH-етап; `playbooks/site.yml` виконує три Ansible playbook. Докладніше: [quickstart](docs/getting-started/QUICKSTART.md).
