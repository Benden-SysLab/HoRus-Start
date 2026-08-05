# HoRus-Start — Платформа IaC для автоматизации Proxmox VE (v2.0-RC1)

🌐 **Языки**: [English](./README.md) | **Русский** | [Українська](./README.uk.md) | [日本語](./README.ja.md) | [Deutsch](./README.de.md) | [Français](./README.fr.md)

---

## 🏛️ Архитектурный обзор и концепция

**HoRus-Start v2** — это промышленный фреймворк автоматизации IaC (Infrastructure-as-Code), предназначенный для развертывания, подготовки и управления кластерами гипервизоров Proxmox VE на bare-metal серверах. Построенный на декларативных принципах, модульных ролях Ansible и версионируемом Runtime API v1 на базе JSON, HoRus-Start обеспечивает полный цикл управления — от первоначальной настройки SSH-связности до распределенных хранилищ и каталога облачных образов.

> 🔒 **Заморозка архитектуры (Architecture Freeze v2.0-RC1)**: Пайплайн HoRus-Start заморожен и строго ограничен **Этапами 0–5**. Пайплайн завершает работу после выполнения Этапа 5 (Asset Preparation & Validation). Ручной импорт Golden-шаблонов, provisioning через Terraform и развертывание приложений выполняются за пределами HoRus-Start.

---

## 🚀 Пайплайн исполнения и этапы системы

HoRus-Start соблюдает строгий 5-шаговый пайплайн на всех этапах:

```
[ Декларативный конфиг ] ──► 1. Discovery ──► 2. Normalization ──► 3. Planning ──► 4. Provisioning ──► 5. Verification & Reports
```

### Обзор этапов

| Этап | Название | Описание | Статус |
| :--- | :--- | :--- | :--- |
| **Stage 0** | **Infrastructure Readiness Gate** | Проверка готовности среды (Preflight), автосоздание шаблонов учетных данных, поиск дисков и валидация хэшей дистрибутивов (`stage0.json`). | **СТАБИЛЕН** |
| **Stage 1** | **Bootstrap Connectivity** | Проверка доступности узлов, генерация локальных ed25519 SSH-ключей, развертывание публичных ключей и валидация беспарольного SSH доступа. | **СТАБИЛЕН** |
| **Stage 2** | **Base System Prep** | Настройка репозиториев APT (Debian 13 Trixie & pve-no-subscription), обновление ядра, установка системных утилит и тюнинг параметров sysctl. | **СТАБИЛЕН** |
| **Stage 3** | **Proxmox Cluster** | Инициализация кластера `pvecm` quorum на узлах, настройка сети corosync. | **СТАБИЛЕН** |
| **Stage 4** | **Storage Prepare** | Безопасный поиск физических дисков (`/dev/disk/by-id/`), проверка безопасности системного диска, планирование, форматирование ext4/ZFS и регистрация PVE хранилищ. | **СТАБИЛЕН** |
| **Stage 5** | **Asset Preparation & Validation** | Загрузка облачных ISO/образов (Ubuntu, Debian, Alpine), драйверов VirtIO, кэша LXC; публикация дистрибутивов в хранилище PVE; проверка хэшей и целостности `qemu-img`. | **СТАБИЛЕН** |

> 🛑 **Остановка пайплайна**: Автоматизация полностью завершается после выполнения Stage 5.

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
├── .github/                 # CI/CD Воркли (сканирование секретов, валидация YAML, ansible-lint)
├── config/                  # Декларативная конфигурация кластера и дисков (SOT)
│   ├── examples/            # Примеры конфигураций cluster, network, storage
│   ├── storage.yml
│   └── image_catalog.yml
├── credentials/             # SSH-ключи и пароли (ИГНОРИРУЮТСЯ В GIT)
├── docs/                    # Архитектурная и эксплуатационная документация
│   ├── architecture/        # Спецификации доменной модели, планировщика и Runtime API
│   ├── getting-started/     # Установка, Быстрый старт, Требования
│   ├── operations/          # Устранение неполадок, Восстановление, Бэкап
│   └── security/            # Модель безопасности, Управление секретами, Threat Model
├── inventory/               # Инвентарь Ansible (hosts.yml)
├── playbooks/               # Плейбуки выполнения (00_*.yml — 04_*.yml)
├── plugins/                 # Пользовательские плагины фильтров и действий Ansible
├── roles/                   # Модульные роли (storage_prepare, proxmox_templates и др.)
├── runtime/                 # Объекты Runtime API v1 (ИГНОРИРУЮТСЯ В GIT)
├── schemas/                 # Схемы JSON для валидации
├── scripts/                 # Скрипты проверки и валидации схем
│   ├── stage0_preflight.py
│   ├── storage_validate.py
│   └── validate_schemas.py
├── horus-start              # Интерактивный CLI-лаунчер
├── SECURITY.md              # Политика безопасности и репортинг уязвимостей
├── CONTRIBUTING.md          # Руководство по вкладу в проект
├── CODE_OF_CONDUCT.md       # Кодекс поведения сообщества
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

# Stage 2: Базовая подготовка системы (Debian 13)
ansible-playbook -i inventory/hosts.yml playbooks/01_base_system_prep.yml

# Stage 3: Настройка кластера Proxmox VE
ansible-playbook -i inventory/hosts.yml playbooks/02_proxmox_cluster.yml

# Stage 4: Подготовка хранилищ (Режим планирования / Dry-run)
ansible-playbook -i inventory/hosts.yml playbooks/03_storage_prepare.yml -e "storage_plan_only=true"

# Stage 4: Подготовка хранилищ (Применение изменений)
ansible-playbook -i inventory/hosts.yml playbooks/03_storage_prepare.yml

# Stage 5: Подготовка и валидация ассетов
ansible-playbook -i inventory/hosts.yml playbooks/04_proxmox_templates.yml
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

Все приватные данные, включая SSH-ключи (`credentials/ssh/*`), пароли, файлы Ansible Vault (`.vault_pass`), `.env` файлы и логи выполнения внесены в `.gitignore`. Автоматическое сканирование секретов (`ggshield`) запускается при каждом push.
