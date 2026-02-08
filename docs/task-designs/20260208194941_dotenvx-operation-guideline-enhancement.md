# タスク設計書: dotenvx 運用ガイドの解像度向上

最終更新: 2026-02-08
- ステータス: 完了(done)
- 作成者: Codex
- レビュー: shogohasegawa
- 対象コンポーネント: docs / scripts
- 関連: docs/ai/playbook-assets/python-project-bootstrap/references/env-and-dotenvx.md
- チケット/リンク: 該当なし

## 0. TL;DR
- 現在の dotenvx 記載は方針レベルに留まり、実際の運用フロー（暗号化、実行、追加、平文混在）が十分に示せていない。
- あなたが提示した運用イメージを基準に、Playbook asset を手順レベルへ拡張する。
- AGENTS 側は詳細手順を持たない方針を維持しつつ、参照導線を明確化する。
- dotenvx 運用を標準とするため、プロジェクト初期化時の `.env.example` 自動生成を廃止する。

## 1. 背景 / 課題
- 現行は「dotenvx で encrypted: 管理」「.env.keys はコミットしない」が中心で、日常運用コマンドが不足している。
- 特に以下の実務判断の説明不足がある。
  - 環境ごとの暗号化手順（`.env.development` / `.env.production`）
  - `dotenvx run -f` での実行方法
  - 新規秘密値の追加時に `dotenvx set` を使う流れ
  - 平文（非機密）と暗号文の混在可否
- `.env.keys` の取り扱いは「コミット禁止」だけでは不十分で、共有チャネルの注意点が明文化されていない。
- `python-project-bootstrap` は `.env.example` を自動生成しており、dotenvx 前提運用と役割が重複している。

## 2. ゴール / 非ゴール
### 2.1 ゴール
- `env-and-dotenvx.md` を、初期化から日常運用まで辿れる手順書に更新する。
- 「何をコミットして良いか / だめか」を明示する。
- 平文と暗号文の混在運用（`encrypted:` プレフィックスで識別）を明記する。
- bootstrap 生成物から `.env.example` を外し、Playbook 記述と整合させる。

### 2.2 非ゴール
- dotenvx 自体の検証コード追加や CI 実装変更。
- 既存プロジェクトの `.env.*` 内容変更。
- 秘密情報管理基盤（Vault/1Password等）の導入判断。

## 3. スコープ / 影響範囲
- 変更対象: dotenvx 運用ドキュメントと bootstrap 生成スクリプト。
- 影響範囲: 今後このテンプレートを使うチームの環境変数運用手順と初期生成物。
- 互換性: `.env.example` が自動生成されなくなる（方針に沿った仕様変更）。
- 依存関係: `scripts/sync_ai_context.py`（canonical 更新時のみ）。

## 4. 要件
### 4.1 機能要件
- dotenvx インストール確認、暗号化、実行、追加の各コマンド例を記載する。
- `.env.development` / `.env.production` / `.env.keys` の責務を明確化する。
- 「暗号化対象（秘密情報）」と「平文許容対象（非機密）」の判断基準を明記する。
- `.env.keys` の共有は安全な私的チャネルのみ可とし、Issue/PR/チャット本文へ貼らないことを明記する。
- プロジェクト初期化時に `.env.example` を生成しない方針へ変更する。

### 4.2 非機能要件 / 制約
- AGENTS.md には詳細手順を重複記載しない（責務分離維持）。
- 例示値は必ずダミーを使用し、秘密値を含めない。
- 既存の canonical → generated の同期フローを維持する。

## 5. 仕様 / 設計
### 5.1 全体方針
- 詳細手順は `docs/ai/playbook-assets/python-project-bootstrap/references/env-and-dotenvx.md` に集約する。
- `python-project-bootstrap` の canonical/生成物/スクリプトから `.env.example` 前提を除去する。

### 5.2 変更点一覧
| 対象 | 変更内容 | 影響 | 備考 |
| --- | --- | --- | --- |
| `docs/ai/playbook-assets/python-project-bootstrap/references/env-and-dotenvx.md` | 手順を実運用レベルに拡張（暗号化/実行/追加/混在運用/共有注意） | dotenvx 運用の解像度向上 | 主変更 |
| `docs/ai/canonical/playbooks/python-project-bootstrap.md` | 検証項目から `.env.example` 前提を削除 | Playbook と運用方針の整合 | 正本更新 |
| `scripts/playbooks/python-project-bootstrap/bootstrap_python_project.py` | `.env.example` 自動生成を削除 | 新規構築時の生成物が方針準拠 | スクリプト更新 |
| `docs/ai/playbooks/python-project-bootstrap.md` | canonical 反映で自動更新 | 参照用 Playbook の同期 | 直接編集しない |

### 5.3 詳細
#### API
- 該当なし。

#### UI
- 該当なし。

#### データモデル / 永続化
- 該当なし。

#### 設定 / 環境変数
- `.env.development` / `.env.production`: 暗号化済み秘密値 + 必要に応じて非機密平文を保持。
- `.env.keys`: 秘密鍵を保持し、Git 管理外。
- `.env.example`: 本運用では原則非採用（必要な場合のみ手動で仕様書として作成）。

### 5.4 代替案と不採用理由
- 代替案A: AGENTS.md に詳細手順を直接追加する。
  - 不採用理由: README/AGENTS/Playbook の責務分離に反する。
- 代替案B: `.env.example` を残し続ける。
  - 不採用理由: dotenvx 前提運用では重複管理になり、更新漏れを招く。

## 6. 移行 / ロールアウト
- ドキュメント更新後、`python3 scripts/sync_ai_context.py` で生成物を同期する。
- ロールバック条件: 既存方針と矛盾する記載や過度な運用負荷が判明した場合。
- ロールバック手順: 変更差分を戻し、同期チェックが通る状態へ戻す。

## 7. テスト計画
- 単体: 記載コマンド・ファイル名が一貫していることを静的レビューで確認。
- 結合: `python3 scripts/sync_ai_context.py --check` を実行。
- 手動: `env-and-dotenvx.md` だけ読んで初期化〜追加運用まで手順が追えることを確認。
- LLM/外部依存: 該当なし。
- 合格条件: 主要運用シナリオ（暗号化、実行、追加、混在、共有注意）が明確に記載され、`.env.example` 非生成が反映されている。

## 8. 受け入れ基準
- dotenvx の基本フローがコピペ可能なコマンドで示されている。
- `.env.keys` をコミットしないだけでなく、共有時の注意が明記されている。
- 暗号文と平文の混在運用のルールが明記されている。
- bootstrap 実装と Playbook 記載から `.env.example` の自動生成前提が除去されている。

## 9. リスク / 対策
- リスク: 「.env.keys をチーム共有可」を誤って広いチャネルで運用して漏えいする。
- 対策: 共有可否ではなく「共有チャネル制約（安全な私的チャネルのみ）」を明記する。

## 10. オープン事項 / 要確認
- 該当なし。

## 11. 実装タスクリスト
- [x] `env-and-dotenvx.md` を手順レベルへ更新する。
- [x] `python-project-bootstrap` 正本から `.env.example` 前提を除去する。
- [x] bootstrap から `.env.example` 自動生成を削除する。
- [x] `sync_ai_context.py` 実行/チェックを実施する。

## 12. ドキュメント更新
- [ ] `README.md`（必要に応じて）
- [ ] `AGENTS.md`（必要に応じて）
- [x] `docs/`（該当ファイルあれば）

## 13. 承認ログ
- 承認者: shogohasegawa
- 承認日時: 2026-02-08 19:52
- 承認コメント: OK.承認

## 実装開始条件
- [x] ステータスが `承認済み(approved)` である
- [x] 10. オープン事項が空である
- [x] 受け入れ基準とテスト計画に合意済み
