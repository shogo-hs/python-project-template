---
name: python-project-bootstrap
description: 新しい Python プロジェクトの初期セットアップを標準化するスキル。AGENTS.md を対話で確定し、Hexagonal Architecture 前提のディレクトリ、SOLID/DRY ガイド、API/タスク設計ドキュメント、`.env.development`/`.env.production` と dotenvx 暗号化運用を整備するときに使う。CI は必須工程とし、品質ゲート設定は必ず `$python-uv-ci-setup` を呼び出して完了させる依頼で適用する。
---

<!-- AUTO-GENERATED FILE. DO NOT EDIT DIRECTLY. -->
<!-- source: docs/ai/canonical/playbooks/python-project-bootstrap.md + scripts/sync_ai_context.py -->

# Pythonプロジェクト初期構築

このスキルは、Python 新規プロジェクトの「最初に揃えるべき構造と運用ドキュメント」を再利用可能な手順で作る。

## 実行ルール

- AGENTS.md の不明点がある状態で雛形を確定しない。必ず対話で埋める。
- 質問は 1〜3 問ずつ行い、回答を反映して次の質問へ進む。
- CI 設定は必須。必ず `$python-uv-ci-setup` を使って完了させる。
- 既存ファイルがある場合は破壊的上書きを避け、差分統合を優先する。
- 生成する `SKILL.md` / `references/` / `agents/openai.yaml` は日本語中心で記述する。
- AGENTS.md は常時有効ルールのみを記載し、長い手順やコマンドは Skill 側へ集約する。
- 原則として新規作成は `.codex/skills` 同梱のテンプレートリポジトリから開始する。
- 空リポジトリから開始する場合のみ、グローバル `python-project-bootstrap` を初回1回だけ使う。
- 初回生成直後に共有 Skill を `<repo>/.codex/skills/` へ配置し、以後は repo ローカルを正本とする。

## 実行フロー

1. 前提を確認する。
- ルートディレクトリと Git 管理状態を確認する。
- 既存の `AGENTS.md`、`docs/tasks` または `docs/task-designs` の有無を確認する。
- 既存構成があれば、パス命名を尊重する。
- 空リポジトリの場合は「初回のみグローバル bootstrap」を適用し、完了後に repo ローカル Skill へ移行する。

2. AGENTS.md 情報を対話で確定する。
- `references/agents-md-checklist.md` の必須項目から埋める。
- `references/agents-skills-boundary.md` を基準に、AGENTS と Skills の責務境界を固定する。
- 未確定項目は既定値を勝手に固定せず、ユーザー確認を優先する。
- 既定値を使う場合は「既定値を採用した」と明示してから確定する。

3. 初期構成を生成する。
- `scripts/bootstrap_python_project.py` を実行して、ディレクトリと初期ドキュメントを生成する。
- 例:
  - `python3 scripts/bootstrap_python_project.py --target <project-root> --project-name <name> --package-name <package_name> --description "<description>"`
- 必要に応じて `--task-design-dir docs/task-designs` や `--force` を使う。
- 生成後に共有 Skill を `<repo>/.codex/skills/` に配置してコミットし、以後の実行基盤を repo ローカルへ固定する。

4. 生成内容をレビューする。
- `references/project-structure.md` を基準に、`adapters/application/domain/ports` の責務分離を確認する。
- `docs/rules/solid/README.md` と `docs/rules/code_architecture/README.md` の導線が AGENTS.md から参照できることを確認する。
- `references/env-and-dotenvx.md` を基準に `.env.*` の運用記載が整合しているか確認する。

5. CI を必須で設定する。
- 生成直後に必ず `$python-uv-ci-setup` を呼び出して、`uv` ベースの品質ゲートと GitHub Actions を整備する。
- 本スキル内で CI 設定を再実装しない（DRY を維持）。

6. 検証する。
- 生成ファイル一覧を確認する。
- `AGENTS.md` の必須セクションが埋まっていることを確認する。
- `.env.development` / `.env.production` / `.env.example` の整合を確認する。
- CI 設定完了後に `uv run pre-commit install` が実行可能な状態であることを確認する。

7. 結果を報告する。
- 作成・更新したファイル
- 対話で確定した項目
- CI 設定の実行結果
- 残課題（手動で埋めるべき値や鍵など）
- 共有スキルの配置先（repo 配下 / 個人グローバル）と採用理由

## 参照ファイル

- AGENTS.md ヒアリング項目: `references/agents-md-checklist.md`
- AGENTS と Skills の責務境界: `references/agents-skills-boundary.md`
- Hexagonal 構成と責務: `references/project-structure.md`
- `.env.*` と dotenvx 暗号化運用: `references/env-and-dotenvx.md`
