# HoRus-Start — Proxmox VE IaC インフラストラクチャプラットフォーム (v2.0-RC1)

🌐 **言語**: [English](./README.md) | [Русский](./README.ru.md) | [Українська](./README.uk.md) | **日本語** | [Deutsch](./README.de.md) | [Français](./README.fr.md)

---

## 🏛️ 概要とコンセプト

**HoRus-Start v2** は、ベアメタル Proxmox VE ハイパーバイザークラスタのブートストラップ、プロビジョニング、管理用に設計されたエンタープライズグレードの IaC (Infrastructure-as-Code) 自動化フレームワークです。宣言的原則、モジュール化された Ansible ロール、およびバージョン管理された JSON Runtime API v1 に基づいて構築されており、ベアメタルネットワーク接続から分散ストレージ、クラウドイメージカタログの公開まで、一貫したライフサイクル管理を提供します。

> 🔒 **アーキテクチャフリーズ通知 (v2.0-RC1)**: HoRus-Start パイプラインは恒久的に**ステージ 0〜5** に限定されています。パイプラインは Stage 5 (Asset Preparation & Validation) の完了をもって終了します。手動での Golden テンプレート作成、Terraform によるプロビジョニング、アプリケーションのデプロイは HoRus-Start のスコープ外で実行されます。手動 Golden テンプレート作成 (VM ID 9000 Base, VM ID 9001 Docker, LXC テンプレートおよび SRE 標準) の詳細手順は [docs/golden-images/](./docs/golden-images/) に記載されています。

---

## 🚀 実行パイプラインとステージ構成

HoRus-Start は、すべての有効なインフラステージで決定論的な 5 ステップのパイプラインを適用します。

```
[ 宣言的設定 ] ──► 1. 検出 (Discovery) ──► 2. 正規化 (Normalization) ──► 3. 計画 (Planning) ──► 4. 適用 (Provisioning) ──► 5. 検証とレポート (Verification & Reports)
```

### ステージ概要

| ステージ | 名称 | 説明 | 状態 |
| :--- | :--- | :--- | :--- |
| **Stage 0** | **Infrastructure Readiness Gate** | 事前検証（Preflight）、資格情報フォーマット、ハードウェアの自動検出、ハッシュ検証、`stage0.json` の発行。 | **安定** |
| **Stage 1** | **Bootstrap Connectivity** | ターゲットノードの接続確認、ローカル ed25519 SSH 鍵の生成、公開鍵のデプロイ、パスワードなし root SSH アクセスの検証。 | **安定** |
| **Stage 2** | **Base System Prep** | APT リポジトリ (Debian 13 Trixie & pve-no-subscription) の設定、カーネル更新、コアツールのインストール、sysctl チューニング。 | **安定** |
| **Stage 3** | **Proxmox Cluster** | ノード間の `pvecm` クォーラムクラスタの初期化、corosync ネットワークリンクの設定。 | **安定** |
| **Stage 4** | **Storage Prepare** | 物理ブロックデバイス (`/dev/disk/by-id/`) の安全な検出、OS ディスクの安全性検証、マウント計画、ext4/ZFS フォーマット、PVE ストレージ登録。 | **安定** |
| **Stage 5** | **Asset Preparation & Validation** | クラウド OS イメージ、ISO カタログ、VirtIO ドライバー、LXC キャッシュのダウンロード、PVE ストレージへの公開、ハッシュおよび `qemu-img` 整合性検証。 | **安定** |

> 🛑 **パイプライン終了**: 自動化は Stage 5 完了後に終了します。

---

## 💾 Stage 4 ストレージフレームワーク

Stage 4 は、実運用水準のストレージ調整エンジンを提供します。

1. **Discovery (検出)**: `lsblk -J` 経由でブロックデバイスをスキャンし、ディスク状態を変更することなく永続的な `/dev/disk/by-id/` シンボリックリンクをマッピングします。
2. **OS ディスクの安全保護**: 対象ストレージがシステム OS 親ドライブ (`/`, `/boot`, `/boot/efi`, `/etc/pve`) と重複しないことを検証します。
3. **Planner (計画)**: 変更差分 (`needs_format`, `needs_mkdir`, `needs_mount`, `needs_pvesm_add`) を計算し、`runtime/plans/storage_plan.json` に保存します。
4. **Provisioning (適用)**: systemd マウントユニットの作成、ファイルシステムの安全なフォーマット、`/etc/fstab` の更新、Proxmox への登録を実行します。
5. **Verification (検証)**: 適用後の監査、`findmnt` によるマウント検証、ドリフト検出、および `runtime/reports/stage4.json` の生成を行います。

---

## 📡 Runtime API v1 およびドメインモデル

HoRus-Start のステージ間連携は **Runtime API v1** によって管理されており、暗黙の依存関係や Ansible 変数への直接依存を排除しています。

- **Config (`config/`)**: 期待される状態 (Desired State) の唯一の情報源。
- **Runtime (`runtime/`)**: 実績および計画状態 (Actual/Planned State) の唯一の情報源。
  - `runtime/discovery/` — 検出されたハードウェアインベントリ。
  - `runtime/facts/` — 正規化されたインフラファクト。
  - `runtime/plans/` — 機械読み取り可能な実行計画。
  - `runtime/reports/` — ドリフト検出および完了レポート。
  - `runtime/cache/`, `runtime/locks/`, `runtime/state/` — 非公開内部状態。

すべての公開 runtime JSON オブジェクトは `schemas/runtime/` のスキーマに準拠し、ヘッダーメタデータ (`api_version: "v1"`, `schema_version: "1.0"`) を含みます。

---

## 📁 リポジトリ構造

```
HoRus-Start/
├── .github/                 # CI/CD ワークフロー（シークレットスキャン、YAML検証、ansible-lint）
├── config/                  # 宣言的クラスタおよびストレージ設定 (SOT)
│   ├── examples/            # cluster, network, storage 設定のサンプル
│   ├── storage.yml
│   └── image_catalog.yml
├── credentials/             # SSH 鍵およびパスワード (GIT 対象外)
├── docs/                    # アーキテクチャ、運用、セキュリティドキュメント
│   ├── architecture/        # ドメインモデル、プランナースペック、Runtime API
│   ├── getting-started/     # インストール、クイックスタート、要件
│   ├── golden-images/       # Golden VM および LXC テンプレート作成ガイド
│   ├── operations/          # トラブルシューティング、リカバリ、バックアップ
│   └── security/            # セキュリティモデル、シークレット管理、脅威モデル
├── inventory/               # Ansible インベントリ定義 (hosts.yml)
├── playbooks/               # 実行プレイブック (00_*.yml 〜 04_*.yml)
├── plugins/                 # カスタム Ansible フィルタ・アクションプラグイン
├── roles/                   # モジュール化されたドメインロール (storage_prepare, proxmox_templates等)
├── runtime/                 # Runtime API v1 オブジェクト (GIT 対象外)
├── schemas/                 # JSON スキーマ
├── scripts/                 # 検証およびスキーマ確認スクリプト
│   ├── stage0_preflight.py
│   ├── storage_validate.py
│   └── validate_schemas.py
├── horus-start              # 対話型 CLI ランチャー
├── SECURITY.md              # セキュリティポリシーと脆弱性報告
├── CONTRIBUTING.md          # 貢献ガイドライン
├── CODE_OF_CONDUCT.md       # コミュニティ行動規範
└── README.md                # メインプライマリドキュメント
```

---

## 🛠️ 使用方法と操作

### 1. 対話型ランチャーの実行
```bash
./horus-start
```

### 2. 各ステージの個別実行
```bash
# Stage 0: Infrastructure Readiness Gate (Preflight Control Plane)
python3 scripts/stage0_preflight.py

# Stage 1: 接続ブートストラップ
ansible-playbook -i inventory/hosts.yml playbooks/00_bootstrap_connectivity.yml

# Stage 2: 基本システム準備 (Debian 13)
ansible-playbook -i inventory/hosts.yml playbooks/01_base_system_prep.yml

# Stage 3: Proxmox クラスタ構築
ansible-playbook -i inventory/hosts.yml playbooks/02_proxmox_cluster.yml

# Stage 4: ストレージ準備 (計画確認 / Dry-run モード)
ansible-playbook -i inventory/hosts.yml playbooks/03_storage_prepare.yml -e "storage_plan_only=true"

# Stage 4: ストレージ準備 (適用実行)
ansible-playbook -i inventory/hosts.yml playbooks/03_storage_prepare.yml

# Stage 5: アセット準備と検証
ansible-playbook -i inventory/hosts.yml playbooks/04_proxmox_templates.yml
```

### 3. 検証スクリプトの実行
```bash
# ストレージ設定およびインベントリの検証
python3 scripts/storage_validate.py

# Runtime API v1 JSON スキーマの検証
python3 scripts/validate_schemas.py
```

---

## 🔒 セキュリティとプライバシー

SSH 秘密鍵 (`credentials/ssh/*`)、パスワード、Ansible Vault パスワード (`.vault_pass`)、`.env` ファイル、および実行ログは `.gitignore` によって厳格に除外されています。自動シークレットスキャン (`ggshield`) がプッシュごとに実行されます。
