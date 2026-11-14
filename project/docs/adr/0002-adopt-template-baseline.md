# ADR 0002: テンプレートの設計の決まりを引き継ぐ

- ステータス: 承認済み(accepted)
- 決定者: このプロジェクトのチーム

## 1. 文脈

- このプロジェクトは [python-project-template](https://github.com/shogo-hs/python-project-template) から copier で作った。
- テンプレートには、層の分け方・品質ゲート・文書の置き方などの決まりと、その理由（テンプレート ADR）がある。

## 2. 決定

- テンプレートの決まりを、そのまま引き継ぐ。
  - 決まりの中身: `AGENTS.md`（常に守る規約）と `pyproject.toml`・`.pre-commit-config.yaml`・`.github/workflows/ci.yml`（機械で守らせる設定）。
  - 理由: テンプレートの `docs/adr/`（本文では「テンプレート ADR 000N」と呼ぶ）。
  - 引き継いだ版: `.copier-answers.yml` の `_commit`。テンプレートの更新を取り込むと、この版も上がる。
- 決まりを外す・変えるときは、このプロジェクトの ADR を足す（例「テンプレート ADR 0007 の複雑さの上限を 15 にする」）。

## 3. 代替案と不採用理由

- 代替案A: テンプレートの ADR をこのリポジトリに写す。
  - 不採用理由: テンプレート自身の経緯（このプロジェクトでは起きていない変更）が、このプロジェクトの判断として読まれてしまう。

## 4. 影響

- テンプレートの更新は template-update スキル（`uvx copier update`）で取り込む。

## 5. フォローアップ

- なし。
