# HoRus-Start

[English](README.md) · [Русский](README.ru.md) · [Українська](README.uk.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [日本語](README.ja.md)

Ansible-проект для первичной настройки четырёх нод Proxmox VE и сборки кластера **HoRus-SysLab**. Рабочий пайплайн настраивает SSH, репозитории APT и базовые пакеты, затем создаёт кластер и проверяет quorum. Проверен на Debian 13 и Proxmox VE 9.2.21.

| Нода | IP управления | Роль |
| --- | --- | --- |
| horus-pmx-node01 | 10.255.0.7 | первая нода кластера |
| horus-pmx-node02 | 10.255.0.8 | присоединяемая нода |
| horus-pmx-node03 | 10.255.0.9 | присоединяемая нода |
| horus-pmx-node04 | 10.255.0.10 | присоединяемая нода |

## Запуск из WSL Debian

На управляющей машине нужны Python 3 и Ansible. Перед запуском проверьте `inventory/hosts.yml`, `config/network.yml`, `config/cluster.yml`, доступ по SSH, TCP 8006 до первой ноды и связь Corosync между нодами.

```bash
cd /path/to/HoRus-Start
export HORUS_SSH_KEY_DIR=/mnt/c/Users/Benden/.ssh/horus/horus-pmx-node

python3 scripts/stage0_preflight.py
ansible-playbook -i inventory/hosts.yml playbooks/00_bootstrap_connectivity.yml
ansible-playbook -i inventory/hosts.yml playbooks/01_base_system_prep.yml
ansible-playbook -i inventory/hosts.yml playbooks/02_proxmox_cluster.yml
```

Stage 0 при первом запуске создаёт ключ Ed25519 вне репозитория. Playbook 00 запрашивает пароли root в терминале, устанавливает публичный ключ и проверяет SSH. Playbook 01 приводит репозитории к Debian Trixie и Proxmox no-subscription, обновляет пакеты. Playbook 02 последовательно добавляет ноды и проверяет Corosync/quorum. Уже включённые ноды повторно не добавляются; пароль root первой ноды запрашивается лишь при необходимости присоединения.

`./horus-start` запускает preflight и SSH-этап. `playbooks/site.yml` запускает три Ansible playbook; на новой управляющей машине сначала отдельно выполните Stage 0.

Закрытый ключ хранится в `~/.ssh/horus/horus-pmx-node` или в каталоге из `HORUS_SSH_KEY_DIR`. Имя ключа по умолчанию — `horus-pmx-cluster`; его можно изменить через `HORUS_SSH_KEY_NAME`. Пароли вводятся во время работы и не записываются в YAML репозитория.

## Границы проекта

Диски, файловые системы, хранилища Proxmox, GPU/PCI passthrough, шаблоны VM и приложения настраиваются отдельно. Успешная сборка кластера не означает готовность дисков или видеокарт.

Локальные отчёты лежат в `runtime/reports/` и игнорируются Git. Проверка: `python3 scripts/validate_schemas.py`. Подробности: [установка](docs/getting-started/INSTALLATION.md), [быстрый старт](docs/getting-started/QUICKSTART.md), [устранение ошибок](docs/operations/TROUBLESHOOTING.md).
