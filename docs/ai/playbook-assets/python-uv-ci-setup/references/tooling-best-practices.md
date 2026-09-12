# ツール設定ベストプラクティス（uv前提）

## 1. uv

- `dependency-groups` を使い、開発依存は `dev` グループにまとめる。
- `uv sync` は既定で `dev` を同期するため、ローカル開発時の追加オプションを最小化できる。
- CI では `uv sync --locked --dev` を使い、`uv.lock` と整合する決定論的インストールに固定する。
- src レイアウトでは `[build-system]` を必ず定義する（推奨は uv 同梱の `uv_build`）。
  無いと `uv sync` がプロジェクト自身をインストールせず、`src/` 配下のパッケージを
  mypy / import-linter / pytest が解決できない。

参考:
- [uv dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/)
- [uv build backend](https://docs.astral.sh/uv/concepts/build-backend/)
- [Using uv in GitHub Actions](https://docs.astral.sh/uv/guides/integration/github/)

## 2. Ruff（format/lint/docstring/セキュリティ）

- formatter と linter を Ruff に統一してツール数を減らす。
- 基本セット（`E4/E7/E9/F/I/UP/B/D`）に次を足す。
  - `S`（flake8-bandit 相当）: `eval` / `subprocess` の shell 実行 / 弱いハッシュなどセキュリティ上の問題。
  - `SIM`（flake8-simplify）と `C4`（comprehensions）: 冗長な書き方の整理。
  - `RUF`（Ruff 固有）: 可変既定値、未使用 `noqa` など。
  - `PTH`（flake8-use-pathlib）: `os.path` より `pathlib` を使う。
- bandit を別ツールとして入れない。`S` 規則で同じ検査ができる。
- `pydocstyle` は `convention = "google"` を指定する。
- docstring は短文 1 行のみで終わらせず、処理概要と利用条件が分かる説明を入れる。
- `Args` / `Returns` / `Raises` は、該当する要素がある場合に記載して入出力と失敗条件を明示する。
- 日本語 docstring の運用では、英語前提になりやすいルール（例: `D400`, `D401`, `D415`）と、
  全角括弧を「紛らわしい文字」として誤検知する `RUF001`〜`RUF003` を除外する。
- パッケージ（`__init__.py`）と `__init__` メソッドの docstring（`D104`, `D107`）は求めない。
  処理意図はモジュール・クラス・関数の docstring に書く。
- テストでは `assert` を使うため `S101` を `tests/**` だけ除外する。
- `docstring-code-format = true` を有効化し、docstring 内コード例も整形対象にする。

参考:
- [Ruff settings](https://docs.astral.sh/ruff/settings/)
- [Ruff rules](https://docs.astral.sh/ruff/rules/)

## 3. mypy（静的型チェック）

- 型チェッカーは `mypy` に固定する。
- 最初から `strict = true` を強制せず、必要なフラグを個別に有効化する。
- 「型ヒント必須」の方針に直接対応するフラグを入れる。
  - `disallow_untyped_defs`: 型ヒントの無い関数定義をエラーにする。
  - `disallow_incomplete_defs`: 一部だけ型ヒントがある関数定義をエラーにする。
  - `strict_equality`: 型が重ならない値どうしの比較をエラーにする。
- テストにも同じ基準を適用する（`tests.*` を override で緩めない）。テスト関数に `-> None` を書くだけで済む。
- src レイアウトでは `mypy_path = "src"` と `explicit_package_bases = true` を設定する。
  無いと editable install と `mypy .` の組み合わせで同じファイルが 2 つのモジュール名で見つかり、チェックが止まる。
- 出力可読性のため `show_error_codes = true` を有効化する。
- 設定は `pyproject.toml` に集約する。

参考:
- [mypy config file](https://mypy.readthedocs.io/en/stable/config_file.html)
- [mypy: mapping file paths to modules](https://mypy.readthedocs.io/en/stable/running_mypy.html#mapping-file-paths-to-modules)

## 4. import-linter（依存方向の検証）

- Hexagonal Architecture の依存方向（`adapters -> application -> ports -> domain`）を `layers` 契約で検証する。
  上に書いた層ほど外側で、上から下へだけ import できる。逆方向の import があると `lint-imports` が失敗する。
- `domain` と `ports` が外部技術（Web フレームワーク、DB クライアント、HTTP クライアント）へ依存しないことを
  `forbidden` 契約で検証する。`include_external_packages = true` にすると、未インストールのパッケージ名でも判定できる。
- 契約は `pyproject.toml` の `[tool.importlinter]` に書き、実行は `uv run lint-imports`。
- 層をまだ作っていないプロジェクトでは、`layers` の要素を `"(ports)"` のように括弧で囲んで省略可能にする。
- 例外を許すときは契約の `ignore_imports` に `a.b -> c.d` の形で書き、理由をコメントに残す。
  例外が増えるなら設計を見直す（契約を緩めるほうが先にならないようにする）。
- 導入直後は、わざと逆方向の import を 1 つ足して失敗することを確かめてから戻す。
  契約が層を見つけられていないときも静かに通ってしまうため、「失敗する」ことの確認が要る。

参考:
- [Import Linter](https://import-linter.readthedocs.io/)
- [Layers contract](https://import-linter.readthedocs.io/en/stable/contract_types.html#layers)

## 5. deptry（依存の衛生）

- `uv run deptry src` で、未使用の宣言依存・宣言されていない import・推移依存への直接 import を検出する。
- `[project.dependencies]` と `[dependency-groups]` を自動で読むため、追加設定なしで動く。
- 誤検知（プラグイン経由でしか import されないパッケージなど）は `[tool.deptry.per_rule_ignores]` で
  規則ごとに除外する。全体を無効化しない。

参考:
- [deptry](https://deptry.com/)

## 6. pytest と coverage

- 互換性重視で `[tool.pytest.ini_options]` を使う。
- `--strict-markers` と `--strict-config` を既定化し、設定ミスを早期検知する。
- `--cov` を `addopts` に入れ、`[tool.coverage.run] branch = true` で分岐カバレッジを計測する。
- `[tool.coverage.report] fail_under` で最低カバレッジを CI の合否にする。初期値は 80。
  実行行が 0 のパッケージは 100% として扱われるため、生成直後のプロジェクトで詰まらない。
- 実行コマンドは `uv run pytest -q` を標準化する。

参考:
- [pytest configuration](https://docs.pytest.org/en/stable/reference/customize.html)
- [coverage.py configuration](https://coverage.readthedocs.io/en/latest/config.html)

## 7. pre-commit

- `pre-commit-hooks` の基本フックを入れる。
  - `detect-private-key`: 秘密鍵のコミットを止める（秘密情報をコミットしない方針の機械的な網）。
  - `check-added-large-files`: 巨大ファイルの誤コミットを止める。
  - `check-toml` / `check-yaml`: 設定ファイルの構文を検査する。
  - `end-of-file-fixer` / `trailing-whitespace`: 行末の整形。
- `uv-pre-commit` の `uv-lock` を有効化し、依存追加時のロック更新漏れを防ぐ。
- ツール実行は `uv run` で統一し、ローカル/CIで同じ依存を使う。
- 実行時間を抑えるため、既定は以下を推奨する。
  - `pre-commit`: `ruff format --check`, `ruff check`, `mypy`, `lint-imports`, `deptry`
  - `pre-push`: `pytest`
- インストール時は hook type を明示する。
  - `uv run pre-commit install --hook-type pre-commit --hook-type pre-push`

参考:
- [pre-commit](https://pre-commit.com/)
- [pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks)
- [uv pre-commit integration](https://docs.astral.sh/uv/guides/integration/pre-commit/)

## 8. GitHub Actions

- `actions/setup-python` と `astral-sh/setup-uv` を組み合わせる。
- `setup-uv` では `enable-cache: true` を使う。
- `permissions: contents: read` をワークフロー全体に置き、書き込みが要るジョブにだけ権限を足す。
- `concurrency` で同じブランチの古い実行を打ち切る。
- `uv sync --locked --dev` の後、`ruff format --check`、`ruff check`、`mypy`、`lint-imports`、`deptry`、`pytest` を順番に実行する。
- 失敗時に原因を分離しやすいよう、ステップを分割する。
- action のメジャーバージョンは導入時点の最新を使い、以後の更新は Dependabot に任せる。

参考:
- [setup-uv action](https://github.com/astral-sh/setup-uv)
- [Using uv in GitHub Actions](https://docs.astral.sh/uv/guides/integration/github/)
- [GITHUB_TOKEN permissions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication)

## 9. Dependabot

- `.github/dependabot.yml` で `github-actions` と `uv` の 2 エコシステムを週次更新にする。
- `groups` でまとめ、週 1 本の PR にする。
- 脆弱性の通知（Dependabot alerts）と自動修正 PR（security updates）はリポジトリ設定で有効化する。
  CI に脆弱性スキャンを入れなくても、既知の脆弱性は GitHub 側から通知される。

参考:
- [Dependabot configuration options](https://docs.github.com/en/code-security/dependabot/working-with-dependabot/dependabot-options-reference)

## 10. 推奨実行順序

1. `uv lock`
2. `uv sync --locked --dev`
3. `uv run pre-commit install --hook-type pre-commit --hook-type pre-push`
4. `uv run pre-commit run --all-files`
5. `uv run pytest -q`

## 11. 改善案（標準より強化する場合）

- 型安全性を強化する場合:
  - `mypy` で `strict = true` へ段階的に移行する。
- CI速度を改善する場合:
  - ジョブ分割（lint/type/test）を行い並列化する。
- 脆弱性を CI でも止めたい場合:
  - `uv audit`（uv 0.11 以降。experimental で仕様が変わりうる）か `pip-audit` をステップに足す。
- ライブラリとして配布する場合:
  - `matrix` で複数の Python バージョンを検証する。
