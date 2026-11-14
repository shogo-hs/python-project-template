# ADR 0009: 開発と CI の Python の版を .python-version で固定する

最終更新: 2026-11-14
- ステータス: 承認済み(accepted)
- 決定者: shogo-hs
- 関連: [ADR 0003](./0003-expand-ci-quality-gates.md), [ADR 0008](./0008-distribute-with-copier.md)

## 1. 文脈

- 生成先の CI は `actions/setup-python` の `python-version-file: pyproject.toml` で、`requires-python`（`>=3.14`）を満たす最新の Python を入れていた。
- Python 3.15 が出たあと、humansim の移行の PR（2026-11-14）で CI が 3.15 を入れ、依存（litellm が使う fastuuid 0.14.0）に 3.15 用の wheel が無くて落ちた。手元の uv は 3.14 を使っていたので、手元と CI で版がずれていた。
- `tools/code_graph.py` は ruff が 3.14 の書き方（括弧なしの `except A, B:`）に整形していて、3.14 より古い Python のプロジェクト（humansim は 3.12 以上）では型の検査に通らなかった。

## 2. 決定

- 生成先に `.python-version`（`3.14`）を置き、CI の setup-python は `python-version-file: .python-version` にする。uv も同じファイルを読むので、手元と CI の版がそろう。版を上げるときは、このファイルを変える。
- `requires-python` は下限のまま（`>=3.14`）にする。上限を付けると、依存を解くときに困る利用者が出るため。
- テンプレート由来の `tools/` と `tests/tools/` は、ruff の `target-version = "py312"` で整形し、3.12 以上の Python で読めるようにする。

## 3. 代替案と不採用理由

- 代替案A: `requires-python` に上限（`<3.15`）を付ける。
  - 不採用理由: 上限を付けると、そのプロジェクトを依存に使う側の解決が難しくなる（Python の版の上限は広く避けられている）。
- 代替案B: CI の `python-version` に `"3.14"` を直接書く。
  - 不採用理由: 手元の uv が使う版と別々に管理することになる。

## 4. 影響

- 生成先に `.python-version` が増える（テンプレートに追従するファイル）。
- 既に生成したプロジェクトは、テンプレートの更新（v1.1.0）を取り込むと入る。

## 5. フォローアップ

- [ ] Python 3.15 に上げるときは、依存が 3.15 の wheel を出しているかを確かめてから `.python-version` を変える。

## 6. 変更履歴

- 2026-11-14: 初版作成。
