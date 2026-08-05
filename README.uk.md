# HoRus-Start — Платформа IaC для автоматизації Proxmox VE

🌐 **Мови**: [English](./README.md) | [Русский](./README.ru.md) | **Українська** | [日本語](./README.ja.md) | [Deutsch](./README.de.md) | [Français](./README.fr.md)

---

## 🏛️ Архітектурний огляд та концепція

**HoRus-Start** — це промисловий фреймворк автоматизації IaC (Infrastructure-as-Code), призначений для розгортання, підготовки та управління кластерами гіпервізорів Proxmox VE на bare-metal серверах. Побудований на декларативних принципах, модульних ролях Ansible та версіонованому Runtime API на базі JSON, HoRus-Start забезпечує повний цикл управління — від початкового налаштування SSH-зв'язності до розподілених сховищ та шаблонів хмарних образів.

> 🔒 **Замороження архітектури (Architecture Freeze)**: Етапи 0–4 повністю функціональні, ідемпотентні та зафіксовані в рамках віхи **Architecture Stabilization Milestone (Pre-Stage 5)**.

---

## 🚀 Пайплайн виконання та етапи системи

HoRus-Start дотримується чіткого 5-крокового пайплайну на всіх етапах:

```
[ Декларативний конфіг ] ──► 1. Discovery ──► 2. Normalization ──► 3. Planning ──► 4. Provisioning ──► 5. Verification & Reports
```

### Огляд етапів

| Етап | Назва | Опис | Статус |
| :--- | :--- | :--- | :--- |
| **Stage 0** | **Infrastructure Readiness Gate** | Безпечна перевірка готовності середовища (Preflight), автостворення шаблонів облікових даних та конфігурацій, пошук дисків та валідація хешів дистрибутивів (`stage0.json`). | **СТАБІЛЬНИЙ** |
| **Stage 1** | **Bootstrap Connectivity** | Перевірка доступності вузлів, генерація ed25519 SSH-ключів, розгортання публічних ключів та валідація безпарольного SSH доступу. | **СТАБІЛЬНИЙ** |
| **Stage 2** | **Base System Prep** | Налаштування репозиторіїв APT (pve-no-subscription), оновлення ядра, встановлення системних утиліт та тюнінг sysctl. | **СТАБІЛЬНИЙ** |
| **Stage 3** | **Proxmox Cluster** | Ініціалізація кластера pvecm quorum на вузлах (`horus-pmx-node01` — `node04`), налаштування мережі corosync. | **СТАБІЛЬНИЙ** |
| **Stage 4** | **Storage Prepare** | Безпечний пошук фізичних дисків (`/dev/disk/by-id/`), перевірка безпеки системного диска, планування, форматування ext4/ZFS та реєстрація PVE сховищ. | **СТАБІЛЬНИЙ** |
| **Stage 5** | **Golden Image Factory** | Завантаження хмарних ISO/образів (Ubuntu, Debian, Alpine), створення Cloud-Init шаблонів ВМ у Proxmox. | *Наступний етап* |
| **Stage 6** | **Platform Bootstrap** | Інфраструктура управління: створення terraform-srv, SSH-ключів, sudo, API Token, сервісних акаунтів. | *Заплановано* |
| **Stage 7** | **Security** | Системна безпека та гарденінг: тюнінг sysctl, sshd, fail2ban (за потреби), motd, limits. | *Заплановано* |
| **Stage 8** | **Verification** | Повний self-test платформи (Cluster, Storage, Images, Templates, Users, SSH, Security, Reports). | *Заплановано* |

---

## 💾 Архітектура підсистеми сховищ (Stage 4)

Stage 4 надає механізми безпечного зведення сховищ до бажаного стану:

1. **Discovery**: Сканує блочні пристрої через `lsblk -J` та зіставляє їх зі стабільними симлінками `/dev/disk/by-id/` без зміни стану дисків.
2. **Захист системного диска**: Перевіряє, щоб цільові диски не перетиналися з системним диском ОС (`/`, `/boot`, `/boot/efi`, `/etc/pve`).
3. **Планувальник (Planner)**: Розраховує точний план змін (`needs_format`, `needs_mkdir`, `needs_mount`, `needs_pvesm_add`) і зберігає його в `runtime/plans/storage_plan.json`.
4. **Застосування (Provisioning)**: Створює mount-юніти systemd, форматує файлові системи, оновлює `/etc/fstab` та реєструє диски в Proxmox VE.
5. **Верифікація**: Проводить аудит після розгортання, перевіряє монтування через `findmnt`, фіксує дрейф конфігурації та генерує `runtime/reports/stage4.json`.

---

## 📡 Runtime API v1 та Доменна модель

Взаємодія між етапами в HoRus-Start регламентується **Runtime API v1**, виключаючи приховані залежності та ненадійні змінні Ansible.

- **Config (`config/`)**: Єдине джерело правди для бажаного стану (Desired State).
- **Runtime (`runtime/`)**: Єдине джерело правди для фактичного та запланованого стану.
  - `runtime/discovery/` — Зібраний інвентар обладнання.
  - `runtime/facts/` — Нормалізовані факти інфраструктури.
  - `runtime/plans/` — Машиночитані плани виконання.
  - `runtime/reports/` — Звіти про дрейф та результати виконання.
  - `runtime/cache/`, `runtime/locks/`, `runtime/state/` — Внутрішній стан етапів.

Усі публічні JSON-об'єкти runtime відповідають схемам у `schemas/runtime/` та містять обов'язкові заголовки (`api_version: "v1"`, `schema_version: "1.0"`).

---

## 📁 Структура репозиторію

```
HoRus-Start/
├── config/                  # Декларативна конфігурація кластера та дисків (SOT)
│   ├── storage.yml
│   └── storage_templates/
├── credentials/             # SSH-ключі та паролі (ІГНОРУЮТЬСЯ В GIT)
├── docs/                    # Архітектурна документація
│   └── architecture/
│       ├── ARCHITECTURE_FREEZE.md
│       ├── DOMAIN_MODEL.md
│       ├── PLANNER_SPEC.md
│       └── RUNTIME_API_V1.md
├── inventory/               # Інвентар Ansible (hosts.yml)
├── playbooks/               # Плейбуки виконання (00_*.yml — 04_*.yml)
├── plugins/                 # Плагіни фільтрів та дій Ansible
├── roles/                   # Модульні ролі (storage_prepare та ін.)
├── runtime/                 # Об'єкти Runtime API v1 (ІГНОРУЮТЬСЯ В GIT)
│   ├── discovery/
│   ├── facts/
│   ├── plans/
│   └── reports/
├── schemas/                 # Схеми JSON для валідації
├── scripts/                 # Скрипти перевірки та валідації схем
│   ├── storage_validate.py
│   └── validate_schemas.py
├── horus-start              # Інтерактивний CLI-лаунчер
└── README.md                # Головна документація
```

---

## 🛠️ Інструкція із запуску

### 1. Запуск інтерактивного лаунчера
```bash
./horus-start
```

### 2. Запуск окремих етапів
```bash
# Stage 0: Infrastructure Readiness Gate (Preflight Control Plane)
python3 scripts/stage0_preflight.py

# Stage 1: Підготовка SSH зв'язності
ansible-playbook -i inventory/hosts.yml playbooks/00_bootstrap_connectivity.yml

# Stage 2: Базова підготовка системи
ansible-playbook -i inventory/hosts.yml playbooks/01_base_system_prep.yml

# Stage 3: Налаштування кластера Proxmox VE
ansible-playbook -i inventory/hosts.yml playbooks/02_proxmox_cluster.yml

# Stage 4: Підготовка сховищ (Режим планування / Dry-run)
ansible-playbook -i inventory/hosts.yml playbooks/03_storage_prepare.yml -e "storage_plan_only=true"

# Stage 4: Підготовка сховищ (Застосування змін)
ansible-playbook -i inventory/hosts.yml playbooks/03_storage_prepare.yml
```

### 3. Перевірка та валідація
```bash
# Валідація конфігурації та інвентаря дисків
python3 scripts/storage_validate.py

# Валідація JSON-схем Runtime API v1
python3 scripts/validate_schemas.py
```

---

## 🔒 Безпека та приватність

Усі приватні дані, включаючи SSH-ключі (`credentials/ssh/*`), паролі Ansible Vault (`.vault_pass`), `.env` файли та тимчасові логи виконання внесені до `.gitignore`. Ніколи не зберігайте секрети у репозиторії.
