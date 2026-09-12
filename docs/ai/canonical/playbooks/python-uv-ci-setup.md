---
name: python-uv-ci-setup
description: uv を使う Python プロジェクトで、format/lint/静的型チェック/依存方向の検証/依存の衛生/テスト/docstring ルールをローカルと GitHub Actions で一貫運用するためのセットアップPlaybook。`pyproject.toml` の `[dependency-groups]` と `[tool.importlinter]`、`.pre-commit-config.yaml`、`.github/workflows/ci.yml`、`.github/dependabot.yml` を新規作成または更新し、`uv run pre-commit install` まで完了させる依頼で使う。
---

# Python uv CIセットアップ

このPlaybookでは、`uv + ruff + mypy + import-linter + deptry + pytest + pre-commit + GitHub Actions` を最小差分で導入し、ローカルとCIの品質ゲートをそろえる。

## 実行フロー

1. 前提を確認する。
- ルートに `pyproject.toml` があるか確認する。なければ `uv init --package --build-backend uv` を提案する。
- `pyproject.toml` に `[build-system]` があるか確認する。src レイアウトでは必須（無いと `src/` 配下を mypy / import-linter / pytest が解決できない）。
- `uv --version` と `python --version` を確認する。
- Git管理下か確認する。未初期化なら `git init` を実行してから進む。

2. 既存設定を監査する。
- `pyproject.toml` の `[dependency-groups]`、`[tool.ruff]`、`[tool.mypy]`、`[tool.pytest.*]`、`[tool.coverage.*]`、`[tool.importlinter]`、`[tool.deptry]` を確認する。
- `.pre-commit-config.yaml`、`.github/workflows/*.yml`、`.github/dependabot.yml` を確認する。
- 既存設定がある場合は上書きせず、重複を避けて統合する。

3. `pyproject.toml` を `uv` 前提で整備する。
- 開発依存を `dependency-groups.dev` に集約する。
- 最低限の開発依存をそろえる: `ruff`, `mypy`, `import-linter`, `deptry`, `pytest`, `pytest-cov`, `pre-commit`。
- ルールは `docs/ai/playbook-assets/python-uv-ci-setup/references/templates.md` の `pyproject.toml` テンプレートを基準にし、既存プロジェクトに合わせて微調整する。
- `[tool.importlinter]` の `your_project` を実際のパッケージ名に置換する。まだ無い層は `"(ports)"` のように括弧で囲んで省略可能にする。
- `forbidden_modules` にプロジェクトで使う外部技術（Web フレームワーク、DB / HTTP クライアント）を足す。

4. pre-commit を設定する。
- `.pre-commit-config.yaml` を作成または更新する。
- `pre-commit-hooks` の基本フック（秘密鍵・巨大ファイル・TOML/YAML 構文・行末）を入れる。
- `uv-pre-commit` の `uv-lock` を入れてロックファイル整合を強制する。
- `uv run` 経由で `ruff format --check`、`ruff check`、`mypy`、`lint-imports`、`deptry` を実行する。
- `pytest` は既定で `pre-push` に配置して開発体験を維持する。全コミットで必須にしたい場合は `stages` を `pre-commit` に変更する。

5. GitHub Actions と Dependabot を設定する。
- `.github/workflows/ci.yml` を作成または更新する。
- `permissions: contents: read` と `concurrency` を置く。
- `actions/setup-python` と `astral-sh/setup-uv` を使い、`uv sync --locked --dev` の後にローカルと同じ 6 本のチェックを実行する。
- キャッシュは `setup-uv` の `enable-cache: true` を基本にする。
- `.github/dependabot.yml` を作成し、`github-actions` と `uv` を週次更新にする。

6. ローカルセットアップを完了する。
- `uv lock`
- `uv sync --locked --dev`
- `uv run pre-commit install --hook-type pre-commit --hook-type pre-push`
- `uv run pre-commit run --all-files`

7. 最終検証を実行する。
- `uv run ruff format --check .`
- `uv run ruff check .`
- `uv run mypy .`
- `uv run lint-imports`
- `uv run deptry src`
- `uv run pytest -q`
- import-linter が層を見つけているか確かめる: `domain` から `adapters` を import する行をわざと 1 つ足し、`uv run lint-imports` が失敗することを確認してから戻す。契約が層を見つけられていないと静かに通ってしまうため、この確認を省略しない。

8. 結果を報告する。
- 追加・更新したファイル
- 実行コマンドと結果（逆依存で失敗した確認を含む）
- 残課題（既存コード由来のlint/type/test失敗、`fail_under` に届かないカバレッジなど）

## 運用ルール

- 型チェックは `mypy` に固定し、`ty` は使わない。
- 型ヒントは必須（`disallow_untyped_defs`）。テストにも同じ基準を適用し、override で緩めない。
- 依存方向（`adapters -> application -> ports -> domain`）と `domain` / `ports` の外部技術への非依存は import-linter で検証する。文書の約束だけにしない。
- import-linter の契約を緩める（`ignore_imports` を足す）ときは理由をコメントに残す。例外が増えるなら設計を見直す。
- docstring は Google style を採用し、短文 1 行のみの記述を避ける。
- docstring の先頭では「何をする処理か」「どの条件で使うか」を日本語で具体的に説明する。
- 引数がある処理は `Args`、戻り値がある処理は `Returns`、例外を送出しうる処理は `Raises` を記載する。
- `pydocstyle` の `convention = "google"` を有効化し、必要に応じて日本語運用に不要なルールのみ最小限で除外する。
- `project.requires-python` を定義し、Ruff のバージョン推論と整合させる。
- カバレッジ閾値（`fail_under`）を下げるときは理由を ADR に残す。
- CI とローカルで実行コマンドを一致させる。

## 参照ファイル

- 設定方針と採用理由: `docs/ai/playbook-assets/python-uv-ci-setup/references/tooling-best-practices.md`
- そのまま適用できる雛形: `docs/ai/playbook-assets/python-uv-ci-setup/references/templates.md`
- 依存方向を機械検証する判断: `docs/adr/0002-enforce-hexagonal-dependencies-with-import-linter.md`
- 品質ゲート拡充の判断: `docs/adr/0003-expand-ci-quality-gates.md`
