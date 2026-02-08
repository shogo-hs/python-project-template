# タスク設計書: Playbook Only Operation

最終更新: 2026-02-08
- ステータス: 完了(done)
- 作成者: Codex
- レビュー: shogo-hs
- 対象コンポーネント: docs
- 関連: `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/README.md`
- チケット/リンク: 該当なし

## 0. TL;DR
- 運用の統一感を高めるため、`.codex/skills` への依存を廃止し、`AGENTS.md + docs/ai/playbooks/*.md` で完結する構成へ移行する。
- `scripts/sync_ai_context.py` から `.codex/skills/*/SKILL.md` の生成を削除し、`docs/ai/playbooks/*.md` と `.cursor/rules/*.mdc` の生成に限定する。
- `.codex/skills` 配下に置いていた参照資料と補助スクリプトを `docs/ai/playbook-assets/` と `scripts/playbooks/` へ移設し、playbook 本文の参照先を更新する。
- `README.md` / canonical 文書 / CI 監視パスを新構成へそろえる。

## 1. 背景 / 課題
- 現状は正本を playbook に寄せた一方で、配布先に `.codex/skills/*/SKILL.md` が残っており、概念として Skill と Playbook が混在している。
- Cursor + Claude では Skill 実行機構がないため、実体としては playbook 参照運用なのに、ドキュメント上は Skill 中心に見えて一貫性が低い。
- `bootstrap_after_canonical.py` など一部処理が `.codex/skills` の物理パスに依存しており、完全移行の障害になっている。

## 2. ゴール / 非ゴール
### 2.1 ゴール
- リポジトリ運用を「AGENTS + Playbooks」に一本化する。
- `.codex/skills` を運用上必須の参照先から外す。
- 既存の `sync_ai_context.py` / `--check` / CI の整合を維持する。

### 2.2 非ゴール
- playbook の手順内容を大幅に書き換えること。
- Python プロジェクト生成ロジック自体（`bootstrap_python_project.py` の機能）を再設計すること。
- 既存コミット履歴の整理や rewrite。

## 3. スコープ / 影響範囲
- 変更対象: 同期スクリプト、README、canonical ルーティング、playbook 参照先、CI、補助スクリプト配置。
- 影響範囲: Codex/Cursor 併用時の運用手順、初期化スクリプト実行パス。
- 互換性: `python3 scripts/sync_ai_context.py` は維持。生成内容のみ変更。
- 依存関係: Python 3.12、既存 `scripts/bootstrap_after_canonical.py`、`docs/ai/canonical/playbooks/*.md`。

## 4. 要件
### 4.1 機能要件
- `scripts/sync_ai_context.py` は以下を生成/検証対象とする。
  - `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/AGENTS.md`
  - `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/.cursor/rules/*.mdc`
  - `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/docs/ai/playbooks/*.md`
- `.codex/skills/*/SKILL.md` の生成を停止する。
- playbook が参照する `references/` / `scripts/` は `.codex/skills` ではなく新配置を参照する。
- `bootstrap_after_canonical.py` は移設後の bootstrap スクリプト位置を参照する。

### 4.2 非機能要件 / 制約
- 自動生成ファイルヘッダ方針を維持する。
- ドキュメント上で「Skill を必須実行基盤とする」記述を残さない。
- CI ドリフト検知で不要な監視（`.codex/skills/**/SKILL.md`）を除外する。

## 5. 仕様 / 設計
### 5.1 全体方針
- ルーティング概念は `playbook id` に統一し、`$skill-name` 記法を廃止する。
- playbook 本文正本は `docs/ai/canonical/playbooks/` に固定し、配布先は `docs/ai/playbooks/` のみとする。
- 補助資料の正本は `docs/ai/playbook-assets/`、実行スクリプトは `scripts/playbooks/` に集約する。

### 5.2 変更点一覧
| 対象 | 変更内容 | 影響 | 備考 |
| --- | --- | --- | --- |
| `docs/ai/canonical/task-routing.md` | ルーティング表記を playbook 基準へ変更 | AGENTS/Cursorルール文言が統一される | 生成元 |
| `scripts/sync_ai_context.py` | `.codex/skills` 出力と `$skill` 解析を削除し playbook id 解析へ変更 | 生成物が簡素化される | 必須 |
| `README.md` | Skill 同梱運用の記述を削除し、Playbook 運用へ一本化 | 利用者理解の改善 | 必須 |
| `.github/workflows/ai-context-sync.yml` | `.codex/skills/**/SKILL.md` の監視を削除 | CI 対象が新構成に一致 | 必須 |
| `scripts/bootstrap_after_canonical.py` | bootstrap スクリプト参照先を新パスへ変更 | 初期化フロー維持 | 必須 |
| `.codex/skills/*/references`, `.codex/skills/*/scripts` | `docs/ai/playbook-assets/`, `scripts/playbooks/` に移設 | 参照元を一本化 | 必須 |
| `.codex/skills/` | 削除（または空ディレクトリ化） | 概念混在を解消 | 最終確認後に実施 |

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
- 代替案A: `.codex/skills` を残しつつ「非推奨」扱いにする。
  - 不採用理由: 物理構成が残る限り、運用者に二重構成を意識させる。
- 代替案B: AGENTS.md へ全手順を直書きし、playbook を削除する。
  - 不採用理由: AGENTS が肥大化し、変更時の差分レビュー効率が下がる。

## 6. 移行 / ロールアウト
- 1PRで移設・生成ロジック更新・ドキュメント更新を同時反映する。
- `python3 scripts/sync_ai_context.py` と `--check` を連続実行し、生成物整合を確認する。
- ロールバック条件: `bootstrap_after_canonical.py` が移設先を解決できず初期化フローが壊れる場合。
- ロールバック手順: `bootstrap_after_canonical.py` の参照先を旧パスへ戻し、移設分を戻す。

## 7. テスト計画
- 単体: `python3 scripts/sync_ai_context.py` の実行成功と生成結果確認。
- 結合: `python3 scripts/sync_ai_context.py --check` 成功。
- 手動: README/AGENTS/Cursor rules から `.codex/skills` 依存文言が消えていることを確認。
- LLM/外部依存: 該当なし。
- 合格条件: 生成と検証が成功し、`rg -n ".codex/skills"` で意図した参照のみ（ゼロ想定）になる。

## 8. 受け入れ基準
- `.codex/skills/*/SKILL.md` が生成対象から外れている。
- `docs/ai/playbooks/*.md` と `.cursor/rules/20-playbooks.mdc` が従来どおり生成される。
- `scripts/bootstrap_after_canonical.py` が移設後スクリプトを使って成功する。
- README と canonical ルーティングが playbook-only 方針で一致している。
- `python3 scripts/sync_ai_context.py --check` が成功する。

## 9. リスク / 対策
- リスク: 移設漏れで playbook 内の参照パスが壊れる。
- 対策: `rg -n "references/|scripts/" docs/ai/canonical/playbooks` で全参照を検査し、存在確認を行う。
- リスク: `.codex/skills` 削除で既存利用者フローが迷う。
- 対策: README に移行方針を明記し、`docs/ai/playbook-assets/` と `scripts/playbooks/` の導線を追加する。

## 10. オープン事項 / 要確認
- 該当なし

## 11. 実装タスクリスト
- [x] playbook 資産の移設（references/scripts）
- [x] `sync_ai_context.py` の playbook-only 化
- [x] canonical/README/CI の記述更新
- [x] `sync` と `--check` の実行確認
- [x] `.codex/skills` の不要物整理

## 12. ドキュメント更新
- [x] `README.md`（必要に応じて）
- [x] `AGENTS.md`（必要に応じて）
- [x] `docs/`（該当ファイルあれば）

## 13. 承認ログ
- 承認者: shogo-hs
- 承認日時: 2026-02-08 15:59
- 承認コメント: OK

## 実装開始条件
- [x] ステータスが `承認済み(approved)` である
- [x] 10. オープン事項が空である
- [x] 受け入れ基準とテスト計画に合意済み
