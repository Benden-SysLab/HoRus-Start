# HoRus-Start — Платформа IaC для автоматизации Proxmox VE

🌐 **Языки**: [English](./README.md) | **Русский** | [Українська](./README.uk.md) | [日本語](./README.ja.md) | [Deutsch](./README.de.md) | [Français](./README.fr.md)

---

## 🏛️ Архитектурный обзор и концепция

**HoRus-Start** — это промышленный фреймворк автоматизации IaC (Infrastructure-as-Code), предназначенный для развертывания, подготовки и управления кластерами гипервизоров Proxmox VE на bare-metal серверах. Построенный на декларативных принципах, модульных ролях Ansible и версионируемом Runtime API на базе JSON, HoRus-Start обеспечивает полный цикл управления — от первоначальной настройки SSH-связности до распределенных хранилищ и шаблонов облачных образов.

> 🔒 **Заморозка архитектуры (Architecture Freeze)**: Этапы 0–4 полностью функциональны, идемпотентны и зафиксированы в рамках вехи **Architecture Stabilization Milestone (Pre-Stage 5)**.

---

## 🚀 Пайплайн исполнения и этапы системы

HoRus-Start соблюдает строгий 5-шаговый пайплайн на всех этапах:

```
[ Декларативный конфиг ] ──► 1. Discovery ──► 2. Normalization ──► 3. Planning ──► 4. Provisioning ──► 5. Verification & Reports
```

### Обзор этапов

| Этап | Название | Описание | Статус |
| :--- | :--- | :--- | :--- |
| **Stage 0** | **Infrastructure Readiness Gate** | Безопасная проверка готовности среды (Preflight), автосоздание шаблонов учетных данных и конфигураций, поиск дисков и валидация хэшей дистрибутивов (`stage0.json`). | **СТАБИЛЕН** |
| **Stage 1** | **Bootstrap Connectivity** | Проверка доступности узлов, генерация ed25519 SSH-ключей, развертывание публичных ключей и валидация беспарольного SSH доступа. | **СТАБИЛЕН** |
| **Stage 2** | **Base System Prep** | Настройка репозиториев APT (pve-no-subscription), обновление ядра, установка системных утилит и тюнинг параметров sysctl. | **СТАБИЛЕН** |
| **Stage 3** | **Proxmox Cluster** | Инициализация кластера pvecm quorum на узлах (`horus-pmx-node01` — `node04`), настройка сети corosync. | **СТАБИЛЕН** |
| **Stage 4** | **Storage Prepare** | Безопасный поиск физических дисков (`/dev/disk/by-id/`), проверка безопасности системного диска, планирование, форматирование ext4/ZFS и регистрация PVE хранилищ. | **СТАБИЛЕН** |
| **Stage 5** | **Golden Image Factory** | Загрузка облачных ISO/образoв (Ubuntu, Debian, Alpine), создание Cloud-Init шаблонов ВМ в Proxmox. | *Следующий этап* |
| **Stage 6** | **Platform Bootstrap** | Инфраструктура управления: создание terraform-srv, SSH-ключей, sudo, API Token, сервисных аккаунтов. | *Запланирован* |
| **Stage 7** | **Security** | Системная безопасность и харденинг: тюнинг sysctl, sshd, fail2ban (при необходимости), motd, limits. | *Запланирован* |
| **Stage 8** | **Verification** | Полный self-test платформы (Cluster, Storage, Images, Templates, Users, SSH, Security, Reports). | *Запланирован* |

---

## 💾 Архитектура подсистемы хранилищ (Stage 4)

Stage 4 предоставляет механизмы безопасного приведения хранилищ к желаемому состоянию:

1. **Discovery**: Сканирует блочные устройства через `lsblk -J` и сопоставляет их со стабильными симлинками `/dev/disk/by-id/` без изменения состояния дисков.
2. **Защита системного диска**: Проверяет, чтобы целевые диски не пересекались с системным диском ОС (`/`, `/boot`, `/boot/efi`, `/etc/pve`).
3. **Планировщик (Planner)**: Рассчитывает точный план изменений (`needs_format`, `needs_mkdir`, `needs_mount`, `needs_pvesm_add`) и сохраняет его в `runtime/plans/storage_plan.json`.
4. **Применение (Provisioning)**: Создает mount-юниты systemd, форматирует файловые системы, обновляет `/etc/fstab` и регистрирует диски в Proxmox VE.
5. **Верификация**: Проводит аудит после развертывания, проверяет монтирование через `findmnt`, фиксирует дрейф конфигурации и генерирует `runtime/reports/stage4.json`.

---

## 📡 Runtime API v1 и Доменная модель

Взаимодействие между этапами в HoRus-Start регламентируется **Runtime API v1**, исключая скрытые зависимости и ненадёжные переменные Ansible.

- **Config (`config/`)**: Единственный источник правды для желаемого состояния (Desired State).
- **Runtime (`runtime/`)**: Единственный источник правды для фактического и планируемого состояния.
  - `runtime/discovery/` — Собранный инвентарь оборудования.
  - `runtime/facts/` — Нормализованные факты инфраструктуры.
  - `runtime/plans/` — Машиночитаемые планы выполнения.
  - `runtime/reports/` — Отчеты о дрейфе и результаты выполнения.
  - `runtime/cache/`, `runtime/locks/`, `runtime/state/` — Внутреннее состояние этапов.

Все публичные JSON-объекты runtime соответствуют схемам в `schemas/runtime/` и содержат обязательные заголовки (`api_version: "v1"`, `schema_version: "1.0"`).

---

## 📁 Структура репозитория

```
HoRus-Start/
├── config/                  # Декларативная конфигурация кластера и дисков (SOT)
│   ├── storage.yml
│   └── storage_templates/
├── credentials/             # SSH-ключи и пароли (ИГНОРИРУЮТСЯ В GIT)
├── docs/                    # Архитектурная документация
│   └── architecture/
│       ├── ARCHITECTURE_FREEZE.md
│       ├── DOMAIN_MODEL.md
│       ├── PLANNER_SPEC.md
│       └── RUNTIME_API_V1.md
├── inventory/               # Инвентарь Ansible (hosts.yml)
├── playbooks/               # Плейбуки выполнения (00_*.yml — 04_*.yml)
├── plugins/                 # Пользовательские плагины фильтров и действий Ansible
├── roles/                   # Модульные роли (storage_prepare и др.)
├── runtime/                 # Объекты Runtime API v1 (ИГНОРИРУЮТСЯ В GIT)
│   ├── discovery/
│   ├── facts/
│   ├── plans/
│   └── reports/
├── schemas/                 # Схемы JSON для валидации
├── scripts/                 # Скрипты проверки и валидации схем
│   ├── storage_validate.py
│   └── validate_schemas.py
├── horus-start              # Интерактивный CLI-лаунчер
└── README.md                # Главная документация
```

---

## 🛠️ Инструкция по запуску

### 1. Запуск интерактивного лаунчера
```bash
./horus-start
```

### 2. Запуск отдельных этапов
```bash
# Stage 0: Infrastructure Readiness Gate (Preflight Control Plane)
python3 scripts/stage0_preflight.py

# Stage 1: Подготовка SSH связности
ansible-playbook -i inventory/hosts.yml playbooks/00_bootstrap_connectivity.yml

# Stage 2: Базовая подготовка системы
ansible-playbook -i inventory/hosts.yml playbooks/01_base_system_prep.yml

# Stage 3: Настройка кластера Proxmox VE
ansible-playbook -i inventory/hosts.yml playbooks/02_proxmox_cluster.yml

# Stage 4: Подготовка хранилищ (Режим планирования / Dry-run)
ansible-playbook -i inventory/hosts.yml playbooks/03_storage_prepare.yml -e "storage_plan_only=true"

# Stage 4: Подготовка хранилищ (Применение изменений)
ansible-playbook -i inventory/hosts.yml playbooks/03_storage_prepare.yml
```

### 3. Проверка и валидация
```bash
# Валидация конфигурации и инвентаря дисков
python3 scripts/storage_validate.py

# Валидация JSON-схем Runtime API v1
python3 scripts/validate_schemas.py
```

---

## 🔒 Безопасность и приватность

Все приватные данные, включая SSH-ключи (`credentials/ssh/*`), пароли Ansible Vault (`.vault_pass`), `.env` файлы и временные логи выполнения внесены в `.gitignore`. Никогда не сохраняйте секреты в репозиторий.
