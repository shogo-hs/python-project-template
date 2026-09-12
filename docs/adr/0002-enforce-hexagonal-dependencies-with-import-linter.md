# ADR 0002: Hexagonal の依存方向を import-linter で機械検証する

最終更新: 2026-09-12
- ステータス: 承認済み(accepted)
- 決定者: shogo-hs
- 関連: `docs/ai/canonical/coding-standards.md`, `docs/ai/canonical/playbooks/python-uv-ci-setup.md`, `docs/ai/playbook-assets/python-uv-ci-setup/references/templates.md`, [ADR 0003](./0003-expand-ci-quality-gates.md)

## 1. 文脈

- 本テンプレートは Hexagonal Architecture（`adapters -> application -> ports -> domain`）を採用し、「domain は外部技術へ依存しない」を設計原則にしている。
- しかし CI が回しているのは ruff / mypy / pytest だけで、依存方向は文書上の約束にとどまっていた。domain から adapters を import しても、ports に HTTP クライアントを持ち込んでも CI は通る。
- AI エージェントが実装する前提のテンプレートなので、文書の約束より機械の網のほうが違反を止めやすい。

## 2. 決定

- [import-linter](https://import-linter.readthedocs.io/) を開発依存に加え、`pyproject.toml` の `[tool.importlinter]` に 2 つの契約を置く。
  - `layers` 契約: `adapters`, `application`, `ports`, `domain` の順で、上から下へだけ import を許す。
  - `forbidden` 契約: `domain` と `ports` から Web フレームワーク・DB / HTTP クライアント（`fastapi`, `sqlalchemy`, `httpx`, `requests`, `boto3` を初期値）への import を禁止する。`include_external_packages = true` で未インストールの名前も判定する。
- `uv run lint-imports` を pre-commit と GitHub Actions の両方に入れ、ローカルと CI で同じ契約を検証する。
- 導入時は逆方向の import をわざと 1 つ足して失敗することを確認してから戻す。契約が層を見つけられていないときは静かに通ってしまうため。
- 優先した要件: 設計原則の違反を PR の段階で止めること。追加ツールは 1 本に抑えること。

## 3. 代替案と不採用理由

- 代替案A: 文書（`docs/rules/code_architecture/README.md`）とレビューで守る。
  - 不採用理由: 現状がこれで、違反を止められていない。レビューは人の注意力に依存する。
- 代替案B: ruff の `flake8-tidy-imports`（`banned-api`）で禁止 import を列挙する。
  - 不採用理由: モジュール単位の禁止は書けるが、層の順序（推移的な依存を含む）は表現できない。
- 代替案C: 自前のスクリプトで `ast` を歩いて import を検査する。
  - 不採用理由: import-linter が同じことを契約の宣言だけで行える。保守対象を増やさない。
- 代替案D: pytest のテストとして依存方向を検査する（`pytest-archon` など）。
  - 不採用理由: 契約が Python コードに埋まり、設定として一覧できない。テストの失敗と設計違反が混ざる。

## 4. 影響

- コードへの影響: `src/<package>/` の各層に `__init__.py` が必要（bootstrap が生成する）。既存プロジェクトで逆依存があると CI が落ちるため、導入時に修正するか `ignore_imports` に理由つきで登録する。
- 運用への影響: `pyproject.toml` に `[build-system]` が必要になる（無いとパッケージが解決できず契約が評価できない）。契約を緩めるときは理由をコメントに残す。
- ドキュメントへの影響: `python-uv-ci-setup` Playbook、`templates.md`、`tooling-best-practices.md`、bootstrap が生成する `docs/rules/code_architecture/README.md`。

## 5. フォローアップ

- [ ] テンプレートから立ち上げたプロジェクトで、`ignore_imports` が増えていないかを定期的に見る。
- [ ] `forbidden_modules` の初期値が実プロジェクトの外部技術と合っているかを見直す。

## 6. 変更履歴

- 2026-09-12: 初版作成。
