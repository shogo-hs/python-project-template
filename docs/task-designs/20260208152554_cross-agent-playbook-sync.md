# タスク設計書: Cross Agent Playbook Sync

最終更新: 2026-02-08
- ステータス: 完了(done)
- 作成者: Codex
- レビュー: shogo-hs
- 対象コンポーネント: docs
- 関連: `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/AGENTS.md`
- チケット/リンク: 該当なし

## 0. TL;DR
- Codex Skill と Cursor(Claude) で手順知識を共通化するため、Skill 本文の正本を `docs/ai/canonical/playbooks/` に集約する。
- `scripts/sync_ai_context.py` を拡張し、同じ正本から `docs/ai/playbooks/`・`.codex/skills/*/SKILL.md`・`.cursor/rules/20-playbooks.mdc` を生成する。
- 既存の `AGENTS.md` と `.cursor/rules/00-global.mdc` / `10-task-routing.mdc` の生成は維持し、CI のドリフト検知対象を追加する。
- これにより実行エンジン差は残しつつ、運用手順の内容管理は単一正本に統一する。

## 1. 背景 / 課題
- 現状は Codex では `.codex/skills/*/SKILL.md` を直接利用できる一方、Cursor で Claude を使うと Skill 機構自体は使えない。
- その結果、同じ運用知識を Codex 側と Cursor 側で重複管理しやすく、更新漏れが起きる。
- テンプレートの目的である「正本を 1 箇所に集約して配布」と、Skill 本文の運用が一致していない。

## 2. ゴール / 非ゴール
### 2.1 ゴール
- Skill 本文の正本を `docs/ai/canonical/playbooks/` に集約する。
- Codex 向け `SKILL.md` と Cursor 向け参照ルールを同一正本から自動生成する。
- `python3 scripts/sync_ai_context.py --check` 1 回で全生成物ドリフトを検知できるようにする。

### 2.2 非ゴール
- `.codex/skills/*/references/` や `scripts/` の全面再設計。
- Cursor に Codex と同等の Skill 実行エンジンを実装すること。
- 各 Skill の手順内容そのものを大きく変更すること。

## 3. スコープ / 影響範囲
- 変更対象: AI 運用ドキュメント、生成スクリプト、CI のドリフト検知対象。
- 影響範囲: Codex 利用者、Cursor/Claude 利用者、テンプレート利用時の初期セットアップ手順。
- 互換性: 既存コマンド `python3 scripts/sync_ai_context.py` は維持。生成対象追加のみ。
- 依存関係: Python 3.12 実行環境、既存 `.codex/skills/*` ディレクトリ構成。

## 4. 要件
### 4.1 機能要件
- `docs/ai/canonical/playbooks/*.md` を新設し、5 Skill 分の本文を保持する。
- `scripts/sync_ai_context.py` が以下を生成/検証できること。
  - `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/docs/ai/playbooks/*.md`
  - `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/.codex/skills/*/SKILL.md`
  - `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/.cursor/rules/20-playbooks.mdc`
- `.cursor/rules/20-playbooks.mdc` に、Cursor 側は共通 playbook を参照して手順適用する運用指示を含める。

### 4.2 非機能要件 / 制約
- 既存の自動生成ヘッダ方針（直接編集禁止）を維持する。
- 生成結果は deterministic（同一入力で同一出力）であること。
- README に運用手順を明示し、手動運用との差異を減らす。

## 5. 仕様 / 設計
### 5.1 全体方針
- 「ポリシー/ルーティング/コーディング標準」に加え、「playbook 本文」も canonical 配下に持たせる。
- `sync_ai_context.py` を単一エントリポイントとして維持し、生成先を増やす。
- 既存 Skill ディレクトリ内の `references/` と `scripts/` は温存し、`SKILL.md` のみ生成管理へ切り替える。

### 5.2 変更点一覧
| 対象 | 変更内容 | 影響 | 備考 |
| --- | --- | --- | --- |
| `docs/ai/canonical/playbooks/*.md` | 5 Skill 分の正本を追加 | 手順の正本が一本化される | 新規ディレクトリ |
| `scripts/sync_ai_context.py` | playbook 読み込みと追加生成ロジックを実装 | 生成対象が増える | 既存出力は維持 |
| `.cursor/rules/20-playbooks.mdc` | playbook 参照ルールを自動生成 | Cursor 側で共通手順参照が可能 | 新規生成物 |
| `docs/ai/playbooks/*.md` | Cursor/Codex 共通の配布用文書を生成 | 閲覧導線が統一 | 新規生成物 |
| `.github/workflows/ai-context-sync.yml` | 監視パスを追加 | CI で新規生成物ドリフト検知 | 必須更新 |
| `README.md` | 新運用フローを追記 | 利用者理解の向上 | 必須更新 |

### 5.3 詳細
#### API
- 該当なし

#### UI
- 該当なし

#### データモデル / 永続化
- 該当なし

#### 設定 / 環境変数
- 該当なし

### 5.4 代替案と不採用理由
- 代替案A: 既存 `.codex/skills/*/SKILL.md` を正本にして Cursor rules を手書き同期する。
  - 不採用理由: Cursor 側との重複管理が残り、更新漏れリスクが解消しない。
- 代替案B: Cursor 側向けに別の手順ドキュメントを新設し、Codex Skill とは分離管理する。
  - 不採用理由: 正本が複数になり、テンプレートの運用原則と矛盾する。

## 6. 移行 / ロールアウト
- 1回の PR で canonical 追加・スクリプト拡張・生成物更新を同時に反映する。
- `python3 scripts/sync_ai_context.py` を実行して生成物を確定し、`--check` で差分ゼロを確認する。
- ロールバック条件: 生成スクリプト変更で既存 `AGENTS.md` / Cursor rules の内容が意図せず壊れた場合。
- ロールバック手順: `scripts/sync_ai_context.py` の追加ロジックを戻し、既存3種生成のみに戻す。

## 7. テスト計画
- 単体: `python3 scripts/sync_ai_context.py` 実行で対象ファイルが更新されることを確認。
- 結合: `python3 scripts/sync_ai_context.py --check` が成功し、CI 想定チェックを通ることを確認。
- 手動: 生成された `AGENTS.md`、`.cursor/rules/*.mdc`、`.codex/skills/*/SKILL.md` の内容整合を目視確認。
- LLM/外部依存: 該当なし（ローカル生成のみ）。
- 合格条件: 新規生成物を含めて `--check` が成功し、README 記載が実装内容と一致する。

## 8. 受け入れ基準
- `docs/ai/canonical/playbooks/` に 5 Skill 分の正本が存在する。
- `python3 scripts/sync_ai_context.py` 実行で `docs/ai/playbooks/`、`.codex/skills/*/SKILL.md`、`.cursor/rules/20-playbooks.mdc` が生成される。
- `python3 scripts/sync_ai_context.py --check` が成功する。
- `.github/workflows/ai-context-sync.yml` が追加生成物の変更を監視する。
- `README.md` に新しい正本/生成先/運用手順が反映される。

## 9. リスク / 対策
- リスク: 既存 `SKILL.md` を生成管理に切り替える際に frontmatter や説明文の差分が出る。
- 対策: 既存本文を canonical へ移植し、生成後差分を目視で突合する。
- リスク: 生成対象拡大で `--check` が壊れる。
- 対策: 実装後に `sync` と `--check` を連続実行し、CI ワークフロー定義と監視パスを同時更新する。

## 10. オープン事項 / 要確認
- 該当なし

## 11. 実装タスクリスト
- [x] canonical playbook 正本ファイルを追加する
- [x] `scripts/sync_ai_context.py` を拡張する
- [x] 生成物（playbooks / skill wrappers / cursor rule）を更新する
- [x] CI ワークフローと README を更新する
- [x] `sync` と `--check` の実行結果を確認する

## 12. ドキュメント更新
- [x] `README.md`（必要に応じて）
- [ ] `AGENTS.md`（必要に応じて）
- [x] `docs/`（該当ファイルあれば）

## 13. 承認ログ
- 承認者: shogo-hs
- 承認日時: 2026-02-08 15:36
- 承認コメント: OK

## 実装開始条件
- [x] ステータスが `承認済み(approved)` である
- [x] 10. オープン事項が空である
- [x] 受け入れ基準とテスト計画に合意済み
