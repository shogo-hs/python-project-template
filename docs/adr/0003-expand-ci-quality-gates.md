# ADR 0003: CI の品質ゲートを ruff / mypy / pytest の 3 本から 6 本へ拡充する

最終更新: 2026-09-12
- ステータス: 承認済み(accepted)
- 決定者: shogo-hs
- 関連: `docs/ai/canonical/playbooks/python-uv-ci-setup.md`, `docs/ai/playbook-assets/python-uv-ci-setup/references/tooling-best-practices.md`, [ADR 0002](./0002-enforce-hexagonal-dependencies-with-import-linter.md)

## 1. 文脈

- `python-uv-ci-setup` Playbook の品質ゲートは ruff format / ruff check / mypy / pytest だった。
- 次の穴があった。
  - pytest-cov は dev 依存に入っているだけで、カバレッジの閾値が無い。
  - 未使用・未宣言の依存を見ていない。
  - mypy が「型ヒント必須」の方針に対して `disallow_untyped_defs` を持たず、型の無い関数が通る。
  - GitHub Actions のバージョンが固定されたまま古くなり（checkout@v5 / setup-python@v6 / setup-uv@v7）、更新する仕組みが無い。
  - bootstrap が `__init__.py` も build-system も生成しないため、生成直後のプロジェクトで `src/` 配下が import できず、CI が赤から始まる。

## 2. 決定

- 品質ゲートを次の 6 本にする: ruff format / ruff check / mypy / import-linter（[ADR 0002](./0002-enforce-hexagonal-dependencies-with-import-linter.md)）/ deptry / pytest（coverage 閾値つき）。
- ruff の規則に `S`（flake8-bandit 相当）・`SIM`・`C4`・`RUF`・`PTH` を足す。日本語 docstring の全角括弧を誤検知する `RUF001`〜`RUF003` と、パッケージ / `__init__` の docstring を求める `D104` / `D107` は除外する。
- mypy に `disallow_untyped_defs` / `disallow_incomplete_defs` / `strict_equality` を足す。テストにも同じ基準を適用する。src レイアウト用に `mypy_path = "src"` と `explicit_package_bases = true` を置く。
- coverage を `branch = true` で計測し、`fail_under = 80` を CI の合否にする。
- pre-commit に `pre-commit-hooks`（秘密鍵・巨大ファイル・TOML/YAML 構文・行末）と import-linter・deptry を足す。
- GitHub Actions は `permissions: contents: read` と `concurrency` を置き、action を現行メジャーに更新する。以後の更新は Dependabot（`github-actions` + `uv`）に任せる。
- build backend は uv 同梱の `uv_build` にする。
- bootstrap は各層と `tests/` に `__init__.py`、smoke テスト、`.gitignore` の coverage 出力を生成し、生成直後に 6 本すべてが通る状態にする。
- 優先した要件: 生成直後に CI が緑であること。ツールを増やしすぎないこと（bandit は ruff の `S` で代替）。ローカルと CI で同じコマンドを使うこと。

## 3. 代替案と不採用理由

- 代替案A: CI に `uv audit` または `pip-audit` を入れて脆弱性を止める。
  - 不採用理由: `uv audit` は uv 0.11 以降の experimental で、実行のたびに preview 警告が出て仕様が変わりうる。`pip-audit` は依存が 1 本増える。既知の脆弱性の通知は GitHub の Dependabot alerts（リポジトリ設定・CI 不要）で受ける。強化したい場合の手順は `tooling-best-practices.md` に残す。
- 代替案B: mypy を `strict = true` にする。
  - 不採用理由: 既存の段階導入方針を維持する。「型ヒント必須」に直接対応する 3 つのフラグだけで目的を満たす。
- 代替案C: bandit を別ツールとして入れる。
  - 不採用理由: ruff の `S` 規則で同じ検査ができる。
- 代替案D: CI を lint / type / test の 3 ジョブに分けて並列化する。
  - 不採用理由: キャッシュが効けば `uv sync` は数秒で、YAML が 3 倍になる利得が無い。ステップ分割で失敗箇所は分かる。
- 代替案E: `__init__.py` にパッケージ docstring を生成して `D104` を満たす。
  - 不採用理由: 定型文を bootstrap で保守することになる。パッケージの docstring は処理意図を書く場所ではない。
- 代替案F: テストを mypy の override で緩める。
  - 不採用理由: 「型ヒント必須」に反する。`tests/` に `__init__.py` が無いと override 自体が効かない。テスト関数に `-> None` を書くだけで済む。
- 代替案G: build backend に hatchling を使う。
  - 不採用理由: `uv_build` は uv 同梱で追加依存が無く、`uv init --package` の既定と一致する。

## 4. 影響

- コードへの影響: 既存プロジェクトに適用すると、型の無い関数・未使用依存・`S` 規則違反・カバレッジ不足で CI が落ちる。段階導入する場合は `ignore` と `fail_under` を一時的に緩め、理由を ADR に残す。
- 運用への影響: 開発依存が 2 本増える（import-linter, deptry）。pre-commit の実行時間が伸びる（実測 14 秒程度、キャッシュ後）。Dependabot の PR が週 1 本届く。
- ドキュメントへの影響: `python-uv-ci-setup` Playbook、`templates.md`、`tooling-best-practices.md`、bootstrap スクリプト、`.github/dependabot.yml`。

## 5. フォローアップ

- [ ] テンプレートから立ち上げたプロジェクトの初回 PR で、GitHub Actions 上で 6 本が通ることを確認する。
- [ ] `fail_under = 80` が実プロジェクトで妥当かを見直す。
- [ ] `uv audit` が experimental を外れたら CI への追加を再検討する。

## 6. 変更履歴

- 2026-09-12: 初版作成。
