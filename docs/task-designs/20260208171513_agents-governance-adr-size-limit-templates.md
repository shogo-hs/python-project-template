# タスク設計書: AGENTS Governance ADR Size Limit Templates

最終更新: 2026-02-08
- ステータス: 完了(done)
- 作成者: Codex
- レビュー: shogo-hs
- 対象コンポーネント: docs
- 関連: `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/AGENTS.md`, `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/docs/ai/canonical/global-policies.md`, `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/docs/ai/canonical/task-routing.md`, `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/scripts/sync_ai_context.py`
- チケット/リンク: 該当なし

## 0. TL;DR
- AGENTS運用の実効性を上げるため、禁止操作・秘密情報取り扱い・例外時停止条件を canonical に追記し、生成物へ反映する。
- 設計判断履歴を残すため ADR 運用を導入し、テンプレートと初期ADRを追加する。
- `sync_ai_context.py` に AGENTS サイズ制約（8KB警告/32KiBハード上限）を追加し、肥大化を検知する。
- AI実行向けに PR/Issue テンプレートを追加し、依頼・レビュー入力の品質を安定化させる。

## 1. 背景 / 課題
- 現行 `AGENTS.md` は方針中心で、禁止コマンドや停止条件の運用境界が弱い。
- 依存追加の手段（`uv add`）を強制する文書化が不足し、`pip install` 系の混入リスクがある。
- 設計判断の記録先がなく、ルール変更理由や採否のトレースが困難。
- PR/Issue テンプレート未整備で、AIが生成する依頼・報告の粒度にばらつきが生じる。
- `AGENTS.md` のサイズ成長を制御する仕組みがなく、将来的なコンテキスト効率低下リスクがある。

## 2. ゴール / 非ゴール
### 2.1 ゴール
- AGENTS生成元に「禁止操作/秘密情報/停止条件」を明示し、再生成で一貫適用できる状態にする。
- ADR の保存先・記載ルール・テンプレートを追加し、初期ADRを1件作成する。
- `sync_ai_context.py` で AGENTS サイズを自動判定し、警告と失敗条件を実装する。
- AI向け PR/Issue テンプレートを導入し、最小必須情報を強制する。

### 2.2 非ゴール
- 既存Playbook全体の全面書き換え。
- CIワークフローの大規模再設計。
- GitHub App/外部SaaS連携の追加。

## 3. スコープ / 影響範囲
- 変更対象: canonicalドキュメント、Playbook追加、ADRドキュメント、同期スクリプト、GitHubテンプレート。
- 影響範囲: AGENTS/Cursor生成結果、ドキュメント運用フロー、PR/Issue作成フロー。
- 互換性: 既存生成フローは維持。AGENTSが32KiB超過時のみ `sync`/`--check` が失敗する。
- 依存関係: `python3 scripts/sync_ai_context.py`、GitHubの標準テンプレート読込機能。

## 4. 要件
### 4.1 機能要件
- `docs/ai/canonical/global-policies.md` に以下を追加する。
  - 依存追加・更新は `uv add` / `uv remove` / `uv sync` を使用し、`pip install` / `uv pip install` を禁止。
  - 秘密情報（APIキー、トークン、秘密鍵）を出力・コミット・平文共有しない。
  - 想定外の大量差分や破壊的操作が必要になった場合は作業停止して再確認する。
- ADR運用を追加する。
  - `docs/adr/README.md` と `docs/adr/0001-record-architecture-decisions.md` を作成。
  - AI向け実行手順として `docs/ai/canonical/playbooks/adr-management.md` を新規追加。
  - `docs/ai/playbook-assets/adr-management/references/_adr-template.md` を追加。
  - `docs/ai/canonical/task-routing.md` に ADR 用ルーティング行を追加。
- `scripts/sync_ai_context.py` に AGENTS サイズ判定を追加する。
  - 警告閾値: 8KB（8192 bytes 超過で WARN）。
  - ハード上限: 32KiB（32768 bytes 超過で ERROR + exit 1）。
- AI向けテンプレートを追加する。
  - `.github/pull_request_template.md`
  - `.github/ISSUE_TEMPLATE/ai-task-request.yml`
  - `.github/ISSUE_TEMPLATE/bug-report.yml`
  - `.github/ISSUE_TEMPLATE/config.yml`

### 4.2 非機能要件 / 制約
- 生成物は直接編集せず canonical 編集後に `sync_ai_context.py` で反映する。
- 追加文書は日本語主体で、既存運用方針（READMEは人向け、AGENTSは実行規約）を崩さない。
- 秘密情報の例示はダミー値のみを使う。

## 5. 仕様 / 設計
### 5.1 全体方針
- ルールは canonical を唯一の編集点とし、AGENTS/Cursorへ自動配布する。
- ADR は「方針変更の履歴と根拠」を残す軽量プロセスとして導入し、変更時に参照しやすい構成にする。
- AIテンプレートは「入力品質の最小要件」を揃えることを目的に、記述を短く固定フォーマット化する。

### 5.2 変更点一覧
| 対象 | 変更内容 | 影響 | 備考 |
| --- | --- | --- | --- |
| `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/docs/ai/canonical/global-policies.md` | 禁止操作/秘密情報/停止条件を追記 | AGENTS/Cursor規約強化 | 生成元 |
| `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/docs/ai/canonical/task-routing.md` | ADR管理Playbookのルーティング追加 | AGENTS/Cursorの導線追加 | 生成元 |
| `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/docs/ai/canonical/playbooks/adr-management.md` | ADR運用Playbookを新規追加 | 実行手順を標準化 | 新規 |
| `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/docs/ai/playbook-assets/adr-management/references/_adr-template.md` | ADR雛形を追加 | 再利用性向上 | 新規 |
| `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/docs/adr/README.md` | ADR運用ガイド追加 | 履歴参照導線を明確化 | 新規 |
| `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/docs/adr/0001-record-architecture-decisions.md` | ADR採用の初期判断を記録 | 運用開始根拠を固定 | 新規 |
| `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/scripts/sync_ai_context.py` | AGENTSサイズ判定（警告/エラー）追加 | コンテキスト肥大を抑制 | 実装修正 |
| `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/.github/pull_request_template.md` | AI向けPRテンプレート追加 | PR品質を平準化 | 新規 |
| `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/.github/ISSUE_TEMPLATE/ai-task-request.yml` | AI向け依頼テンプレート追加 | 依頼品質を平準化 | 新規 |
| `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/.github/ISSUE_TEMPLATE/bug-report.yml` | バグ報告テンプレート追加 | 再現情報の欠落を防止 | 新規 |
| `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/.github/ISSUE_TEMPLATE/config.yml` | テンプレート運用設定追加 | 運用統制を明確化 | 新規 |

### 5.3 詳細
#### API
- 該当なし

#### UI
- 該当なし

#### データモデル / 永続化
- 該当なし

#### 設定 / 環境変数
- 新規環境変数は追加しない。

### 5.4 代替案と不採用理由
- 代替案A: AGENTS.md を直接手編集する。
  - 不採用理由: 自動生成方針と矛盾し、再生成で消失する。
- 代替案B: ADRは README の1セクションで代替する。
  - 不採用理由: 時系列の履歴管理と採否理由の追跡に不向き。
- 代替案C: AGENTSサイズ制御をCIだけで実装する。
  - 不採用理由: ローカル実行時に早期検知できない。

## 6. 移行 / ロールアウト
- 1PRで canonical更新、Playbook/ADR/テンプレート追加、同期スクリプト更新、再生成、検証まで完了する。
- ロールバック条件: `sync_ai_context.py` が失敗し生成整合が崩れる場合。
- ロールバック手順: 追加差分を取り消し、`python3 scripts/sync_ai_context.py --check` が通る状態へ戻す。

## 7. テスト計画
- 単体: `python3 -m py_compile scripts/sync_ai_context.py`
- 結合: `python3 scripts/sync_ai_context.py` 実行後に `python3 scripts/sync_ai_context.py --check`
- 手動:
  - `AGENTS.md` に禁止操作/秘密情報/停止条件が反映されること。
  - `docs/ai/playbooks/adr-management.md` が生成され、`.cursor/rules/20-playbooks.mdc` に参照が追加されること。
  - `.github` のPR/Issueテンプレートが作成されること。
- LLM/外部依存: 該当なし
- 合格条件: すべてのコマンド成功、生成ドリフトなし、追加ファイルの記載内容が要件を満たす。

## 8. 受け入れ基準
- AGENTS生成結果に `uv add` 利用必須と `pip install` / `uv pip install` 禁止が明記される。
- AGENTS生成結果に秘密情報取り扱いルールと例外時停止条件が明記される。
- ADR関連ファイルとADR管理Playbookが追加され、ルーティングから参照できる。
- `sync_ai_context.py` が AGENTS 8KB超過で警告、32KiB超過で失敗する。
- AI向けPR/Issueテンプレートが追加される。
- `python3 scripts/sync_ai_context.py --check` が成功する。

## 9. リスク / 対策
- リスク: ルール追加で AGENTS が過度に肥大化する。
- 対策: サイズ警告を導入し、詳細手順はPlaybookへ委譲する。
- リスク: 新規Playbook追加漏れで `sync_ai_context.py` 実行時に欠損エラーが出る。
- 対策: `task-routing.md` と `canonical/playbooks/` を同時更新し、再生成と`--check`を必須実行する。
- リスク: Issueフォームが現場運用と合わず入力負荷になる。
- 対策: 必須項目を最小化し、AIが埋めやすい短文フィールドを採用する。

## 10. オープン事項 / 要確認
- 該当なし

## 11. 実装タスクリスト
- [x] canonicalへガードレール方針を追記
- [x] ADR管理Playbookとテンプレートを追加
- [x] `docs/adr` を追加して初期ADRを作成
- [x] `sync_ai_context.py` にサイズ判定を実装
- [x] AI向けPR/Issueテンプレートを追加
- [x] 生成更新と検証を実行

## 12. ドキュメント更新
- [x] `README.md`（必要に応じて）
- [x] `AGENTS.md`（必要に応じて）
- [x] `docs/`（該当ファイルあれば）

## 13. 承認ログ
- 承認者: shogo-hs
- 承認日時: 2026-02-08 17:22
- 承認コメント: OK

## 実装開始条件
- [x] ステータスが `承認済み(approved)` である
- [x] 10. オープン事項が空である
- [x] 受け入れ基準とテスト計画に合意済み
