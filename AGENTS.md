# AGENTS.md

<!-- AUTO-GENERATED FILE. DO NOT EDIT DIRECTLY. -->
<!-- source: docs/ai/canonical/* + scripts/sync_ai_context.py -->

## このファイルについて
- このファイルは自動生成です。直接編集しないでください。
- 変更は `docs/ai/canonical/` を編集し、`python3 scripts/sync_ai_context.py` を実行してください。

## 1. グローバルポリシー
- 本リポジトリの AI 運用は「正本を1箇所に集約し、生成先へ配布する」方式を採用する。
- ルール更新時は `docs/ai/canonical/` を編集し、生成ファイルは直接編集しない。
- タスク開始時は必ずタスク設計を作成し、承認後に実装する。
- 既存の実装・ドキュメントとの整合を保ち、変更理由を記録する。
- ユーザーとのコミュニケーションは日本語で行う。
- CI は必須とし、品質ゲートの不一致を許容しない。

## 2. タスクルーティング
- 実装前設計: `$task-design-gate`
- Python の CI / 品質ゲート導入: `$python-uv-ci-setup`
- 新規プロジェクト初期構築: `$python-project-bootstrap`
- API 仕様同期: `$api-spec-sync`
- コミット実行: `$git-commit`

## 使い分けルール

- AGENTS.md には「いつどの Skill を使うか」だけを書く。
- 詳細コマンド・分岐・復旧手順は各 Skill の `SKILL.md` と `references/` を正本にする。
- 同じ手順を AGENTS.md と Skill に重複記載しない。

## 3. コーディング標準
## 設計

- SOLID と DRY を基本原則にする。
- Hexagonal Architecture を採用し、`adapters/application/domain/ports` の責務を分離する。
- 依存方向は外側から内側へ固定し、domain は外部技術へ依存しない。

## Python

- Python 3.12+ を前提にする。
- 型ヒントを必須にし、`mypy` で検証する。
- `ruff` で format/lint を統一する。
- docstring は日本語で簡潔に書く。

## 環境変数

- `.env.development` / `.env.production` を利用する。
- 秘密情報は dotenvx の `encrypted:` 形式で管理する。
- `.env.keys` はコミットしない。
