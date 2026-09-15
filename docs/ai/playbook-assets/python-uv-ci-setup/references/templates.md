# テンプレート集（uv + ruff + mypy + import-linter + deptry + pytest + pre-commit + GitHub Actions）

## 目次

- [1. pyproject.toml（推奨テンプレート）](#1-pyprojecttoml推奨テンプレート)
- [2. .pre-commit-config.yaml（推奨テンプレート）](#2-pre-commit-configyaml推奨テンプレート)
- [3. .github/workflows/ci.yml（推奨テンプレート）](#3-githubworkflowsciyml推奨テンプレート)
- [4. .github/dependabot.yml（推奨テンプレート）](#4-githubdependabotyml推奨テンプレート)
- [5. セットアップ実行コマンド](#5-セットアップ実行コマンド)

## 1. pyproject.toml（推奨テンプレート）

`your-project` はプロジェクト名、`your_project` は `src/` 配下のパッケージ名に置換する。

```toml
[project]
name = "your-project"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[build-system]
requires = ["uv_build>=0.10.0,<0.13.0"]
build-backend = "uv_build"

[dependency-groups]
dev = [
  "deptry>=0.25",
  "import-linter>=2.15",
  "mypy>=2.0",
  "pre-commit>=4.0",
  "pytest>=9.0",
  "pytest-cov>=7.0",
  "ruff>=0.16",
]

[tool.ruff]
line-length = 100

[tool.ruff.format]
docstring-code-format = true

[tool.ruff.lint]
select = ["E4", "E7", "E9", "F", "I", "UP", "B", "D", "S", "SIM", "C4", "RUF", "PTH"]
ignore = [
  # パッケージ（__init__.py）と __init__ メソッドには docstring を求めない
  "D104", "D107",
  # Google style と日本語 docstring の運用に合わない規則
  "D203", "D213", "D400", "D401", "D415",
  # 全角括弧などを「紛らわしい文字」として誤検知する（日本語 docstring 前提では除外）
  "RUF001", "RUF002", "RUF003",
]

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["D100", "D101", "D102", "D103", "D104", "S101"]

[tool.mypy]
python_version = "3.12"
mypy_path = "src"
explicit_package_bases = true
warn_unused_configs = true
warn_return_any = true
warn_unused_ignores = true
check_untyped_defs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
strict_equality = true
show_error_codes = true
pretty = true

[tool.pytest.ini_options]
minversion = "8.0"
addopts = "-ra --strict-markers --strict-config --cov --cov-report=term-missing"
testpaths = ["tests"]

[tool.coverage.run]
branch = true
source = ["src"]

[tool.coverage.report]
fail_under = 80

[tool.importlinter]
root_package = "your_project"
include_external_packages = true

[[tool.importlinter.contracts]]
name = "Hexagonal layers: adapters -> application -> ports -> domain"
type = "layers"
containers = ["your_project"]
layers = ["adapters", "application", "ports", "domain"]

[[tool.importlinter.contracts]]
name = "domain / ports do not depend on external technology"
type = "forbidden"
source_modules = ["your_project.domain", "your_project.ports"]
forbidden_modules = ["fastapi", "sqlalchemy", "httpx", "requests", "boto3"]
```

適用メモ:
- `[build-system]` は必須。無いと `uv sync` がプロジェクト自身をインストールせず、`src/` 配下のパッケージを
  mypy / import-linter / pytest が解決できない。`uv init --package --build-backend uv` が生成する値に合わせてよい。
- `requires-python` を更新したら `tool.mypy.python_version` も合わせる。
- Ruff は `project.requires-python` から推論可能なため、`target-version` は必要時のみ明示する。
- 既存プロジェクトで docstring 違反が多い場合は、`D` ルールを段階導入する。
- docstring は短文 1 行で終わらせず、概要と入出力が分かる情報を含める。
- `Args` / `Returns` / `Raises` は、該当する要素がある場合に必ず記載する。
- `tool.mypy.mypy_path` と `explicit_package_bases` は src レイアウト用。無いと editable install と
  `mypy .` の組み合わせで「同じファイルが 2 つのモジュール名で見つかる」エラーになる。
- `[tool.importlinter]` の `layers` は上に書いた層ほど外側で、上から下へだけ import できる。
  まだ存在しない層は `"(ports)"` のように括弧で囲むと省略可能になる。
- `forbidden_modules` はプロジェクトで使う外部技術（DB クライアント、HTTP クライアント、Web フレームワーク）に
  合わせて増やす。未インストールの名前を書いても動作する。
- `fail_under` は初期値。プロジェクトの実態に合わせて上げる（下げるときは理由を ADR に残す）。
- deptry は追加設定なしで動く。誤検知があるときだけ `[tool.deptry.per_rule_ignores]` で個別に除外する。

docstring 記載例（Google style）:

```python
def publish_report(title: str, dry_run: bool = False) -> str:
    """レポートを公開し、公開済みまたは公開予定の URL を返す。

    指定されたタイトルでレポートを作成する。`dry_run` が `True` の場合は
    永続化を行わず、生成予定の URL のみを返す。

    Args:
        title: 公開するレポートのタイトル。
        dry_run: `True` の場合は保存処理を実行しない。

    Returns:
        公開済み、または公開予定のレポート URL。

    Raises:
        ValueError: `title` が空文字の場合。
    """
```

## 2. .pre-commit-config.yaml（推奨テンプレート）

```yaml
minimum_pre_commit_version: "3.7.0"
default_install_hook_types: [pre-commit, pre-push]

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: check-added-large-files
      - id: check-toml
      - id: check-yaml
      - id: detect-private-key
      - id: end-of-file-fixer
      - id: trailing-whitespace

  - repo: https://github.com/astral-sh/uv-pre-commit
    rev: 0.12.13
    hooks:
      - id: uv-lock

  - repo: local
    hooks:
      - id: ruff-format
        name: ruff format --check
        entry: uv run ruff format --check .
        language: system
        pass_filenames: false

      - id: ruff-lint
        name: ruff check
        entry: uv run ruff check .
        language: system
        pass_filenames: false

      - id: mypy
        name: mypy
        entry: uv run mypy .
        language: system
        pass_filenames: false

      - id: import-linter
        name: import-linter
        entry: uv run lint-imports
        language: system
        pass_filenames: false

      - id: deptry
        name: deptry
        entry: uv run deptry src
        language: system
        pass_filenames: false

      - id: pytest
        name: pytest
        entry: uv run pytest -q
        language: system
        pass_filenames: false
        stages: [pre-push]
```

適用メモ:
- すべてのコミットで `pytest` を必須にする場合は `stages` を削除する。
- フックの実行対象を絞る場合は `files` を追加する。
- `rev` は導入時点の最新タグ。以後の更新は `uv run pre-commit autoupdate` で行う。

## 3. .github/workflows/ci.yml（推奨テンプレート）

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v7

      - name: Set up Python
        uses: actions/setup-python@v7
        with:
          python-version-file: pyproject.toml

      - name: Set up uv
        uses: astral-sh/setup-uv@v10.1.0
        with:
          enable-cache: true

      - name: Sync dependencies
        run: uv sync --locked --dev

      - name: Ruff format check
        run: uv run ruff format --check .

      - name: Ruff lint
        run: uv run ruff check .

      - name: Mypy
        run: uv run mypy .

      - name: Import Linter
        run: uv run lint-imports

      - name: Deptry
        run: uv run deptry src

      - name: Pytest
        run: uv run pytest -q
```

適用メモ:
- `uv.lock` がない場合は先に `uv lock` を実行してコミットする。
- Python複数バージョン検証が必要なら `matrix` を追加する。
- `permissions` は最小権限（読み取りのみ）。カバレッジのコメント投稿などで書き込みが要るジョブは、そのジョブにだけ権限を足す。
- `concurrency` は同じブランチへの連続 push で古い実行を打ち切る。

## 4. .github/dependabot.yml（推奨テンプレート）

```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      actions:
        patterns: ["*"]

  - package-ecosystem: "uv"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      python:
        patterns: ["*"]
```

適用メモ:
- `uv.lock` をコミットしていることが前提（`uv` エコシステムはロックファイルを更新する）。
- 脆弱性の通知（Dependabot alerts）はこのファイルではなくリポジトリ設定で有効化する。
- `groups` で週 1 本の PR にまとめている。個別 PR にしたい依存は `patterns` から外す。

## 5. セットアップ実行コマンド

```bash
uv add --dev ruff mypy import-linter deptry pytest pytest-cov pre-commit
uv lock
uv sync --locked --dev
uv run pre-commit install --hook-type pre-commit --hook-type pre-push
uv run pre-commit run --all-files
```

最終確認:

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy .
uv run lint-imports
uv run deptry src
uv run pytest -q
```
