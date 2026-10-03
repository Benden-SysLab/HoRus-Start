# HoRus-Start

[English](README.md) · [Русский](README.ru.md) · [Українська](README.uk.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [日本語](README.ja.md)

4 台の Proxmox VE ノードを初期設定し、**HoRus-SysLab** クラスタを構成する Ansible プロジェクトです。SSH、Debian/Proxmox の APT リポジトリ、基本パッケージを設定した後、クラスタとクォーラムを検証します。Debian 13 と Proxmox VE 9.2.21 で実行確認済みです。

ノード: `horus-pmx-node01` — `10.255.0.7`、`node02` — `10.255.0.8`、`node03` — `10.255.0.9`、`node04` — `10.255.0.10`。

## WSL Debian から実行

Python 3 と Ansible が必要です。実行前に `inventory/hosts.yml`、`config/network.yml`、`config/cluster.yml` を確認してください。

```bash
export HORUS_SSH_KEY_DIR=/mnt/c/Users/Benden/.ssh/horus/horus-pmx-node
python3 scripts/stage0_preflight.py
ansible-playbook -i inventory/hosts.yml playbooks/00_bootstrap_connectivity.yml
ansible-playbook -i inventory/hosts.yml playbooks/01_base_system_prep.yml
ansible-playbook -i inventory/hosts.yml playbooks/02_proxmox_cluster.yml
```

Stage 0 は必要に応じて外部の Ed25519 鍵を作成します。Playbook 00 は端末で root パスワードを求め、SSH を設定します。Playbook 01 は Debian Trixie と Proxmox no-subscription のリポジトリとパッケージを設定します。Playbook 02 はノードを順番に追加し、クォーラムを検証します。再実行時には既存ノードをスキップします。ローカルレポートは `runtime/reports/` に保存され、Git の対象外です。

ディスク、GPU、Proxmox ストレージ、VM テンプレート、アプリケーションは別途設定します。`./horus-start` は事前確認と SSH を実行し、`playbooks/site.yml` は 3 つの Ansible playbook を実行します。詳細は [クイックスタート](docs/getting-started/QUICKSTART.md) を参照してください。
