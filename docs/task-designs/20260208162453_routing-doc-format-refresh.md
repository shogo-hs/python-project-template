# タスク設計書: Routing And Documentation Ownership Refresh

最終更新: 2026-02-08
- ステータス: 完了(done)
- 作成者: Codex
- レビュー: shogo-hs
- 対象コンポーネント: docs
- 関連: `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/docs/ai/canonical/task-routing.md`, https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes, https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors, https://agents.md/, https://openai.com/index/introducing-codex/
- チケット/リンク: 該当なし

## 0. TL;DR
- `task-routing.md` の記述を「skills風の箇条書き」から「判定テーブル中心」に変更し、読み手が判断条件と参照先を一目で理解できる形にする。
- 生成スクリプト `scripts/sync_ai_context.py` は新フォーマット（テーブル）を「Playbookドキュメントのリンク」からルーティング抽出できるよう拡張し、既存の箇条書きも後方互換で扱う。
- `README.md` と `AGENTS.md` の責務境界（何を書くべきか / 何を書かないべきか）を明文化し、AGENT が最初に読む導線へ配置する。
- 生成物（`AGENTS.md` / `.cursor/rules/10-task-routing.mdc` / `.cursor/rules/20-playbooks.mdc`）を再生成し、`--check` が成功することを確認する。

## 1. 背景 / 課題
- 現行のルーティングは `- ラベル: \`playbook-id\`` 形式で、参照先ドキュメントが文中に現れず、判断根拠と遷移先が読み取りづらい。
- 一方で同期スクリプトはこの記法に依存しており、単純にドキュメント書式を変えると生成が壊れる。
- README と AGENTS の境界が明文化されておらず、運用が進むと「人向け情報」と「エージェント向け実行指示」が混在しやすい。
- 可読性改善と生成の安定性を同時に満たす必要がある。

## 2. ゴール / 非ゴール
### 2.1 ゴール
- ルーティング文書を「ケース / 適用条件 / Playbookドキュメントリンク」などの情報構造で表現する。
- 同期スクリプトが新フォーマットを解釈し、既存生成物との整合を維持する。
- README と AGENTS の記載責務を、運用時に迷いが出ない粒度で明文化する。
- `python3 scripts/sync_ai_context.py` と `python3 scripts/sync_ai_context.py --check` が成功する。

### 2.2 非ゴール
- 各 Playbook 本文の手順内容を変更すること。
- Playbook ファイル名（`task-design-gate.md` など）自体を改名すること。
- 運用全体を Playbook 以外の仕組みに置き換えること。
- 新しいドキュメント管理ツール（Docsサイト、別DBなど）を導入すること。

## 3. スコープ / 影響範囲
- 変更対象: `docs/ai/canonical/task-routing.md`、`docs/ai/canonical/global-policies.md`、`scripts/sync_ai_context.py`、`README.md`、再生成される `AGENTS.md` と `.cursor/rules/*.mdc`。
- 影響範囲: AI 実行時のルーティング参照体験、生成スクリプトの抽出ロジック。
- 影響範囲: ドキュメント更新時の責務判断（README に書くか、AGENTS に書くか）。
- 互換性: 箇条書き形式を残して後方互換を維持し、既存テンプレート利用者への破壊的変更を避ける。
- 依存関係: `docs/ai/canonical/playbooks/*.md` と `docs/ai/playbooks/*.md` の対応関係。

## 4. 要件
### 4.1 機能要件
- `task-routing.md` にルーティング判定テーブルを導入する。
- 同期スクリプトは以下のどちらでもルーティング抽出できること。
  - 新テーブル行形式（`docs/ai/playbooks/*.md` への Markdown リンク）
  - 既存箇条書き形式（後方互換）
- 抽出した順序で `.cursor/rules/20-playbooks.mdc` の参照一覧を生成する。
- `docs/ai/canonical/global-policies.md` に README/AGENTS 書き分け方針（責務境界）を追加し、生成後の `AGENTS.md` へ確実に反映されること。
- `README.md` には人向け概要として「README と AGENTS の役割分担」を簡潔に記載し、詳細指示は AGENTS に委譲すること。

### 4.2 非機能要件 / 制約
- 既存の自動生成ヘッダ仕様を維持する。
- ドキュメントの主言語は日本語のままにする。
- CI の `sync --check` に通ること。

## 5. 仕様 / 設計
### 5.1 全体方針
- 人向け可読性はテーブルで改善し、機械抽出は `docs/ai/playbooks/*.md` へのリンク列を基準に行う。
- 抽出ロジックは「テーブル優先、該当なしなら箇条書きフォールバック」とする。
- ドキュメント責務境界の正本は `docs/ai/canonical/global-policies.md` に置く（理由: `AGENTS.md` と `.cursor/rules/00-global.mdc` の両方へ自動反映され、AGENT が最初に読む導線に入るため）。
- `README.md` は「人向けの入口ドキュメント」に限定し、エージェント実行ルールは `AGENTS.md` を正本とする。

### 5.2 変更点一覧
| 対象 | 変更内容 | 影響 | 備考 |
| --- | --- | --- | --- |
| `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/docs/ai/canonical/task-routing.md` | ルーティング記述をテーブル中心へ変更 | AGENTS/Cursorの表示品質向上 | 生成元 |
| `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/docs/ai/canonical/global-policies.md` | README/AGENTS の責務境界ポリシーを追加 | AGENTの迷いを低減 | 生成元 |
| `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/scripts/sync_ai_context.py` | ルーティング抽出でテーブル行を解釈する正規表現を追加 | 生成安定性維持 | 後方互換あり |
| `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/README.md` | 人向けの書き分け指針と参照導線を追加 | 利用者の編集判断が明確化 | 手動編集 |
| `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/AGENTS.md` | 再生成で新書式を反映 | 利用時の可読性向上 | 自動生成 |
| `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/.cursor/rules/10-task-routing.mdc` | 再生成で新書式を反映 | Cursor参照時の理解向上 | 自動生成 |
| `/Users/shogohasegawa/Documents/New project/templates/codex-cursor-python-template/.cursor/rules/20-playbooks.mdc` | 参照先一覧を新抽出結果で再生成 | ルーティング整合性維持 | 自動生成 |

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
- 代替案A: 箇条書きのまま説明文だけ追加する。
  - 不採用理由: 見出しと本文が増えるだけで判断軸が構造化されず、読みやすさ改善が限定的。
- 代替案B: ルーティング定義を別YAML化し、Markdownへ埋め込む。
  - 不採用理由: 管理ファイルが増え、テンプレートの簡潔さを損なう。
- 代替案C: README に詳細運用ルールを集約し、AGENTS は最小化する。
  - 不採用理由: エージェント向け実行指示が人向け説明に埋もれ、指示の発見性が低下する。

### 5.5 ベストプラクティス調査結果（反映方針）
- GitHub Docs の README 指針では、README はプロジェクトの目的・価値・開始方法・サポート導線など「最初に見る人向け情報」を中心にすべきとされる。
- 同じ GitHub Docs では、寄稿手順など詳細ルールは `CONTRIBUTING.md` など別ドキュメントへ分離し、README から参照する運用が推奨される。
- AGENTS.md 側は AGENTS.md 標準（agents.md）と OpenAI Codex 公式説明の両方で、テスト実行や開発ルールなど「エージェント実行時の具体指示」を置く位置として整理されている。
- 以上を踏まえ、本テンプレートでは「README=人向け入口」「AGENTS=エージェント実行規約」を明示分離し、AGENT が迷わないよう正本を canonical global policy に置く。

## 6. 移行 / ロールアウト
- 同一PRで canonical とスクリプト更新、生成物更新、動作確認を実施する。
- ロールバック条件: 新抽出ロジックで playbook 参照一覧が空または不正になる場合。
- ロールバック手順: テーブル抽出ロジックを戻し、箇条書き抽出のみへ復帰する。

## 7. テスト計画
- 単体: `python3 scripts/sync_ai_context.py` 実行で生成が成功することを確認。
- 結合: `python3 scripts/sync_ai_context.py --check` が成功することを確認。
- 手動: 生成後の `AGENTS.md` と `.cursor/rules/10-task-routing.mdc` がテーブル表記になっていることを確認。
- 手動: `README.md` と `AGENTS.md` の双方に書き分け指針があり、内容が矛盾していないことを確認。
- LLM/外部依存: 該当なし。
- 合格条件: 抽出ルートが欠落せず、`--check` が通る。

## 8. 受け入れ基準
- `docs/ai/canonical/task-routing.md` が skills風の箇条書き中心ではなく、判定テーブル中心の表現になっている。
- `scripts/sync_ai_context.py` が新フォーマットを抽出できる。
- `AGENTS.md`、`.cursor/rules/10-task-routing.mdc`、`.cursor/rules/20-playbooks.mdc` が再生成され、内容が整合している。
- `AGENTS.md` に README/AGENTS 書き分け基準が明示され、AGENT が実行ルール参照先を迷わない。
- `README.md` が人向け入口としての内容に限定され、エージェント実行規約は AGENTS 側へ誘導されている。
- `python3 scripts/sync_ai_context.py --check` が成功する。

## 9. リスク / 対策
- リスク: テーブル抽出の正規表現が誤検知し、不要行を Playbook として解釈する。
- 対策: Markdown リンク記法を必須にし、リンク先を `docs/ai/playbooks/[a-z0-9-]+.md` に限定して抽出する。
- リスク: 既存の箇条書き形式しかない派生テンプレートで互換性が壊れる。
- 対策: 既存正規表現を残し、フォールバック抽出を維持する。

## 10. オープン事項 / 要確認
- 該当なし

## 11. 実装タスクリスト
- [x] `task-routing.md` をテーブル中心へ改訂
- [x] `global-policies.md` に README/AGENTS の責務境界を追加
- [x] `sync_ai_context.py` のルーティング抽出を拡張
- [x] `README.md` に人向け書き分け導線を追記
- [x] 生成物を再生成して反映
- [x] `sync` / `--check` で検証

## 12. ドキュメント更新
- [x] `README.md`（必要に応じて）
- [x] `AGENTS.md`（必要に応じて）
- [x] `docs/`（該当ファイルあれば）

## 13. 承認ログ
- 承認者: shogo-hs
- 承認日時: 2026-02-08 16:33
- 承認コメント: OK

## 実装開始条件
- [x] ステータスが `承認済み(approved)` である
- [x] 10. オープン事項が空である
- [x] 受け入れ基準とテスト計画に合意済み
