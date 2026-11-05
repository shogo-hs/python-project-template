# ADR 0005: 設計の正本をコードにし、設計書は作らず ADR だけを残す

最終更新: 2026-11-05
- ステータス: 承認済み(accepted)
- 決定者: shogo-hs
- 関連: [ADR 0001](./0001-record-architecture-decisions.md), [ADR 0002](./0002-enforce-hexagonal-dependencies-with-import-linter.md)

## 1. 文脈

- これまではタスクごとの設計書（`docs/task-designs/`）、手書きの API 文書（`docs/api/`）、設計ルール文書（`docs/rules/`・`docs/architecture/`）を git で管理し、`task-design-gate` と `api-spec-sync` の手順書で更新を求めていた。
- これらはコードと同じ事実を二重に書く。コードだけが変わると文書が古くなり、エージェントが古い文書を指示として読んで混乱する。
- 依存方向は既に import-linter の契約（コード側）で検証しており、`docs/architecture/` はその内容を文章で繰り返していた。
- `docs/product/` の goals・milestones・progress は状態の列を持ち、進捗は git の履歴と Issue でも分かるので二重管理になっていた。

## 2. 決定

- 設計の正本はコードとする。設計判断の理由だけを `docs/adr/` に残す。
- `task-design-gate` と `api-spec-sync` の手順書・テンプレート・スクリプトを削除する。実装前の承認は AGENTS.md の「方針を示して承認を取る。計画は保存しない」で行う。
- bootstrap は `docs/rules/`・`docs/architecture/`・`docs/api/`・タスク設計ディレクトリ・AGENTS.md を生成しない。
- `docs/product/` は `vision.md`（目的・対象ユーザー・成功状態。コードからは分からない）だけを残し、goals・milestones・progress を削除する。

## 3. 代替案と不採用理由

- 代替案A: 設計書を残し、CI で更新を強制する。
  - 不採用理由: 文書に差分があることしか検査できず、内容がコードと合っているかは保証できない。
- 代替案B: API 仕様を手で書き続ける。
  - 不採用理由: FastAPI などはコードから OpenAPI を出せる。

## 4. 影響

- 既存プロジェクトで設計書を持っているなら、残すべき判断を ADR に移してから消す。

## 5. 変更履歴

- 2026-11-05: 新規作成
