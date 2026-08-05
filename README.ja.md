# HoRus-Start — Proxmox VE IaC インフラストラクチャプラットフォーム

🌐 **言語**: [English](./README.md) | [Русский](./README.ru.md) | [Українська](./README.uk.md) | **日本語** | [Deutsch](./README.de.md) | [Français](./README.fr.md)

---

## 🏛️ 概要とコンセプト

**HoRus-Start** は、ベアメタル Proxmox VE ハイパーバイザークラスタのブートストラップ、プロビジョニング、管理用に設計されたエンタープライズグレードの IaC (Infrastructure-as-Code) 自動化フレームワークです。宣言的原則、モジュール化された Ansible ロール、およびバージョン管理された JSON Runtime API に基づいて構築されており、ベアメタルネットワーク接続から分散ストレージ、クラウドイメージのデプロイメントまで、エンドツーエンドのライフサイクル管理を提供します。

> 🔒 **アーキテクチャフリーズ通知 (Architecture Freeze)**: ステージ 0〜4 は完全かつ冪等に動作し、**Architecture Stabilization Milestone (Pre-Stage 5)** のもとで固定されています。

---

## 🚀 実行パイプラインとステージ構成

HoRus-Start は、すべてのインフラステージで決定論的な 5 ステップのパイプラインを適用します。

```
[ 宣言的設定 ] ──► 1. 検出 (Discovery) ──► 2. 正規化 (Normalization) ──► 3. 計画 (Planning) ──► 4. 適用 (Provisioning) ──► 5. 検証とレポート (Verification & Reports)
```

### ステージ概要

| ステージ | 名称 | 説明 | 状態 |
| :--- | :--- | :--- | :--- |
| **Stage 0** | **Infrastructure Readiness Gate** | 読み取り専用事前検証（Preflight）、資格情報・ストレージテンプレートの自動生成、ハードウェアの自動検出、配布物のハッシュ検証、`stage0.json` の発行。 | **安定** |
| **Stage 1** | **Bootstrap Connectivity** | ターゲットノードの接続確認、ed25519 SSH 鍵の生成、公開鍵のデプロイ、およびパスワードなし root SSH アクセスの検証。 | **安定** |
| **Stage 2** | **Base System Prep** | APT リポジトリ (pve-no-subscription) の設定、カーネル更新、コアツールセットのインストール、および sysctl チューニング。 | **安定** |
| **Stage 3** | **Proxmox Cluster** | ノード間 (`horus-pmx-node01` 〜 `node04`) の pvecm クォーラムクラスタの初期化、corosync ネットワークリンクの設定。 | **安定** |
| **Stage 4** | **Storage Prepare** | 物理ブロックデバイス (`/dev/disk/by-id/`) の safe な検出、OS ディスクの安全性検証、マウント計画、ext4/ZFS フォーマット、および PVE ストレージ登録。 | **安定** |
| **Stage 5** | **Golden Image Factory** | クラウド OS イメージ (Ubuntu, Debian, Alpine) のダウンロードと Proxmox Cloud-Init VM テンプレートの作成。 | *次ステージ* |
| **Stage 6** | **Platform Bootstrap** | プラットフォームの初期ブートストラップと基盤サービスの構築。 | *計画中* |
| **Stage 7** | **Security** | セキュリティの強化、アクセス制御、証明書管理およびセキュリティポリシーの適用。 | *計画中* |
| **Stage 8** | **Verification** | デプロイ後の検証、ソフトウェアスタックおよびユーザーアカウントの設定検証。 | *計画中* |

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
├── config/                  # 宣言的クラスタおよびストレージ設定 (SOT)
│   ├── storage.yml
│   └── storage_templates/
├── credentials/             # SSH 鍵およびパスワード (GIT 対象外)
├── docs/                    # アーキテクチャドキュメント
│   └── architecture/
│       ├── ARCHITECTURE_FREEZE.md
│       ├── DOMAIN_MODEL.md
│       ├── PLANNER_SPEC.md
│       └── RUNTIME_API_V1.md
├── inventory/               # Ansible インベントリ定義 (hosts.yml)
├── playbooks/               # 実行プレイブック (00_*.yml 〜 04_*.yml)
├── plugins/                 # カスタム Ansible フィルタ・アクションプラグイン
├── roles/                   # モジュール化されたドメインロール (storage_prepare 等)
├── runtime/                 # Runtime API v1 オブジェクト (GIT 対象外)
│   ├── discovery/
│   ├── facts/
│   ├── plans/
│   └── reports/
├── schemas/                 # JSON スキーマ
├── scripts/                 # 検証およびスキーマ確認スクリプト
│   ├── storage_validate.py
│   └── validate_schemas.py
├── horus-start              # 対話型 CLI ランチャー
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

# Stage 2: 基本システム準備
ansible-playbook -i inventory/hosts.yml playbooks/01_base_system_prep.yml

# Stage 3: Proxmox クラスタ構築
ansible-playbook -i inventory/hosts.yml playbooks/02_proxmox_cluster.yml

# Stage 4: ストレージ準備 (計画確認 / Dry-run モード)
ansible-playbook -i inventory/hosts.yml playbooks/03_storage_prepare.yml -e "storage_plan_only=true"

# Stage 4: ストレージ準備 (適用実行)
ansible-playbook -i inventory/hosts.yml playbooks/03_storage_prepare.yml
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

SSH 秘密鍵 (`credentials/ssh/*`)、Ansible Vault パスワード (`.vault_pass`)、`.env` ファイル、および一時ログは `.gitignore` によって厳格に除外されています。認証情報をバージョン管理にコミットしないでください。
