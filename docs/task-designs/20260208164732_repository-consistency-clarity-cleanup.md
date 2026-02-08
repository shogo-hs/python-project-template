# タスク設計書: Repository Consistency Clarity Cleanup

最終更新: 2026-02-08
- ステータス: 完了(done)
- 作成者: Codex
- レビュー: shogo-hs
- 対象コンポーネント: docs
- 関連: `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/README.md`, `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/scripts/sync_ai_context.py`, `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/scripts/playbooks/python-project-bootstrap/bootstrap_python_project.py`
- チケット/リンク: 該当なし

## 0. TL;DR
- 現状実装を横断確認し、実パス不一致・方針文言の衝突・テンプレート重複によるドリフトリスクを解消する。
- `api-spec-sync` のチェックリスト表記、`python-project-bootstrap` のタスク設計ディレクトリ方針、Cursor向け文言を整合させる。
- `bootstrap_python_project.py` は playbook-assets の正本テンプレートを優先参照する形へ改善し、重複定義を減らす。
- 変更後に生成更新とドリフト検証を実施し、生成物整合を確認する。

## 1. 背景 / 課題
- API 同期チェックリストのコマンドパスが実装ファイル位置と不一致で、手順どおりに実行できない箇所がある。
- `docs/task-designs` 固定方針と `docs/tasks` 併記が混在し、運用判断がぶれる。
- `bootstrap_python_project.py` がタスク設計/APIテンプレートを独自に内包しており、playbook-assets 正本との乖離が起きやすい。
- Cursor 向け自動生成ルールに「正本として参照」という文言があり、canonical 正本との意味重複が読み手に誤解を与える。

## 2. ゴール / 非ゴール
### 2.1 ゴール
- 参照パス・方針文言・テンプレート参照元を repo 内で一貫させる。
- ブートストラップ時に生成されるタスク設計/API雛形を playbook-assets 正本へ寄せる。
- `sync` と `--check` が成功し、生成物が更新済み状態になる。

### 2.2 非ゴール
- Playbook 全文の大規模リライト。
- アーキテクチャ方針そのものの変更。
- 新規Playbookの追加。

## 3. スコープ / 影響範囲
- 変更対象: canonical playbooks、playbook-assets、同期スクリプト、bootstrap スクリプト。
- 影響範囲: ドキュメント参照手順、初期構築時の生成テンプレート品質、Cursorルール文言。
- 互換性: 既存 CLI は維持。既存 `docs/tasks` プロジェクトは後方互換を残す。
- 依存関係: `python3 scripts/sync_ai_context.py` の生成フロー。

## 4. 要件
### 4.1 機能要件
- `docs/ai/playbook-assets/api-spec-sync/references/sync-checklist.md` のコマンド例を実装パスへ修正する。
- `docs/ai/canonical/playbooks/python-project-bootstrap.md` と関連参照資料の `docs/tasks` 併記を整理する。
- `scripts/playbooks/python-project-bootstrap/bootstrap_python_project.py` で task/API テンプレートの正本参照ロードを実装する。
- `scripts/sync_ai_context.py` の Cursor 向け表現を「実行時参照先」へ修正する。

### 4.2 非機能要件 / 制約
- 生成物は手編集せず、canonical 更新後に `sync_ai_context.py` で再生成する。
- 既存の自動生成ヘッダ方針を維持する。
- Python 3.12+ 互換を崩さない。

## 5. 仕様 / 設計
### 5.1 全体方針
- 「正本は canonical、実行時参照は playbooks」の役割分離を文言で明確化する。
- ブートストラップ生成の雛形は、可能な限り `docs/ai/playbook-assets` から読み込んで重複を減らす。
- 既存資産との互換を保つため、`docs/tasks` は legacy fallback として扱う。

### 5.2 変更点一覧
| 対象 | 変更内容 | 影響 | 備考 |
| --- | --- | --- | --- |
| `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/docs/ai/playbook-assets/api-spec-sync/references/sync-checklist.md` | 実行コマンドのパス修正 | 手順の実行性向上 | ドキュメント修正 |
| `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/docs/ai/canonical/playbooks/python-project-bootstrap.md` | タスク設計ディレクトリ方針を整理 | 方針の一貫性向上 | 生成元 |
| `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/docs/ai/playbook-assets/python-project-bootstrap/references/agents-md-checklist.md` | ヒアリング項目の併記整理 | 対話時の迷い低減 | 参照資料 |
| `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/scripts/playbooks/python-project-bootstrap/bootstrap_python_project.py` | テンプレート正本参照の導入、fallback整理 | ドリフト防止、可読性向上 | 実装修正 |
| `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/scripts/sync_ai_context.py` | Cursor向け文言を明確化 | 正本概念の誤解防止 | 実装修正 |

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
- 代替案A: 既存の重複テンプレートを維持し、文言だけ修正する。
  - 不採用理由: 今後の差分再発を防げない。
- 代替案B: `docs/tasks` 対応を完全削除する。
  - 不採用理由: 既存プロジェクト互換を壊す可能性がある。

## 6. 移行 / ロールアウト
- 1PRで canonical 更新、スクリプト改善、生成物更新、検証を実施する。
- ロールバック条件: 生成更新で `--check` が失敗する場合。
- ロールバック手順: 当該変更を差し戻し、`sync_ai_context.py --check` が通る状態へ戻す。

## 7. テスト計画
- 単体: `python3 -m py_compile scripts/sync_ai_context.py scripts/playbooks/api-spec-sync/check_api_docs_sync.py scripts/playbooks/python-project-bootstrap/bootstrap_python_project.py`
- 結合: `python3 scripts/sync_ai_context.py` 実行後に `python3 scripts/sync_ai_context.py --check`。
- 手動: 生成された `docs/ai/playbooks/python-project-bootstrap.md` と `.cursor/rules/20-playbooks.mdc` の表記整合を確認。
- LLM/外部依存: 該当なし。
- 合格条件: コマンド成功、生成ドリフトなし、主要矛盾点が解消されている。

## 8. 受け入れ基準
- API 同期チェックリストのコマンドで実ファイルを直接実行できる。
- `python-project-bootstrap` 関連文書のタスク設計ディレクトリ方針が一貫している。
- ブートストラップ生成テンプレートが playbook-assets 正本優先で取得される。
- Cursor ルール文言で canonical 正本と矛盾しない。
- `sync_ai_context.py --check` が成功する。

## 9. リスク / 対策
- リスク: テンプレート読み込みパス変更で bootstrap が実行環境依存になる。
- 対策: 正本が見つからない場合は既存内蔵テンプレートへフォールバックさせる。
- リスク: canonical 修正後に生成物未更新で CI が落ちる。
- 対策: 実装後に `sync` と `--check` を必ず連続実行する。

## 10. オープン事項 / 要確認
- 該当なし

## 11. 実装タスクリスト
- [x] 参照パス不一致の修正
- [x] python-project-bootstrap 関連文書の表記統一
- [x] bootstrap スクリプトのテンプレート参照改善
- [x] 生成スクリプト文言の明確化
- [x] 生成更新と検証

## 12. ドキュメント更新
- [ ] `README.md`（必要に応じて）
- [ ] `AGENTS.md`（必要に応じて）
- [x] `docs/`（該当ファイルあれば）

## 13. 承認ログ
- 承認者: shogo-hs
- 承認日時: 2026-02-08 16:47
- 承認コメント: 「現状の実装を網羅的に確認し、矛盾や複雑な箇所、わかりにくい表記などがあれば修正・改善」を依頼

## 実装開始条件
- [x] ステータスが `承認済み(approved)` である
- [x] 10. オープン事項が空である
- [x] 受け入れ基準とテスト計画に合意済み
