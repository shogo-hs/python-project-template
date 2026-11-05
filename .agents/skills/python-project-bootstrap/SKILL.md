---
name: python-project-bootstrap
description: このテンプレートから作った新しい Python プロジェクトを立ち上げる手順。docs/product/vision.md をユーザーと対話で埋め、Hexagonal Architecture のパッケージ骨組み・smoke テスト・.env.example を生成し、python-uv-ci-setup で CI まで整える。新規プロジェクトの初期セットアップを頼まれたときに使う。
---

# Python プロジェクトの立ち上げ

## 実行ルール

- 質問は 1〜3 問ずつ行い、回答を要約して合意を取ってから次へ進む。
- 既定値を使うときは「既定値を採用した」と明示する。
- 既存ファイルは上書きしない（生成スクリプトも上書きしない）。
- CI の設定は必須。この手順の中で再実装せず、`python-uv-ci-setup` を使う。

## 実行フロー

1. 前提を確認する。
   - リポジトリのルートにいること、git 管理下であることを確かめる。

2. プロジェクトの基本情報を確定する。
   - プロジェクト名、一行の説明、パッケージ名（既定: プロジェクト名の snake_case）。
   - `README.md` の冒頭をプロジェクトの説明に書き換える。

3. `docs/product/vision.md` を対話で埋める。
   - このプロダクトで最初に価値を届けたい対象ユーザーは誰か。
   - そのユーザーのどの課題を最優先で解決するか。
   - どの状態になれば価値を届けられたと判断するか。
   - 決まらない項目は `仮置き` と書き、いつ見直すかを残す。

4. 骨組みを生成する。
   - `python3 .agents/skills/python-project-bootstrap/scripts/bootstrap.py --project-name <name> [--package-name <package>]`
   - 生成物: `src/<package>/` の各層と `__init__.py`、`tests/unit/test_smoke.py`、`.env.example`、`.gitignore` への追記。
   - 層の責務は `references/project-structure.md` を基準にする。

5. CI を設定する。
   - `python-uv-ci-setup` を使い、`pyproject.toml`・`.pre-commit-config.yaml`・`.github/workflows/ci.yml`・`.github/dependabot.yml` を整える。

6. 結果を報告する。
   - 作成・更新したファイル、対話で確定した項目、CI の実行結果、残課題。

## 参照ファイル

- Hexagonal 構成と層の責務: `references/project-structure.md`
