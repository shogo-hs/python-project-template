# ADR 一覧

このディレクトリは、テンプレート自身の設計判断（テンプレート ADR）を保存する。生成したプロジェクトには写らない（ADR 0008）。生成先の ADR は `project/docs/adr/` から始まる。

## 目的

- 設計判断の背景・採否理由・影響を時系列で追跡可能にする。
- ルール変更時に「なぜそうしたか」を再確認できるようにする。

## 命名規則

- 形式: `NNNN-short-title.md`
- 例: `0001-record-architecture-decisions.md`
- `NNNN` は 4 桁連番を使用する。

## ステータス

- `提案(proposed)`
- `承認済み(accepted)`
- `却下(rejected)`
- `置換済み(superseded)`

## 作成ルール

- 新規ADRは `project/.agents/skills/adr-management/references/_adr-template.md` を利用する。
- 1ADR には 1 つの判断だけを記載する。
- 既存判断を置換した場合は、新旧ADRの双方に相互リンクを張る。

## ADR 一覧

- [0001: ADR運用を導入して設計判断を記録する](./0001-record-architecture-decisions.md) - 承認済み(accepted)
- [0002: Hexagonal の依存方向を import-linter で機械検証する](./0002-enforce-hexagonal-dependencies-with-import-linter.md) - 承認済み(accepted)
- [0003: CI の品質ゲートを ruff / mypy / pytest の 3 本から 6 本へ拡充する](./0003-expand-ci-quality-gates.md) - 承認済み(accepted)
- [0004: AGENTS.md と .agents/skills を直接の正本にし、Cursor 対応と生成スクリプトをやめる](./0004-agents-md-and-shared-skills.md) - 承認済み(accepted)
- [0005: 設計の正本をコードにし、設計書は作らず ADR だけを残す](./0005-code-as-design-source-of-truth.md) - 承認済み(accepted)
- [0006: dotenvx をやめ、.env.example をコミットして .env はコミットしない](./0006-env-example-instead-of-dotenvx.md) - 承認済み(accepted)
- [0007: PR ごとにコードの関係の差分をレビューする人に出し、関数の複雑さを CI で止める](./0007-review-relation-diff-and-complexity-gate.md) - 承認済み(accepted)
- [0008: 配り方を GitHub のテンプレートリポジトリから copier に移し、生成物を project/ に分ける](./0008-distribute-with-copier.md) - 承認済み(accepted)
- [0009: 開発と CI の Python の版を .python-version で固定する](./0009-pin-python-version.md) - 承認済み(accepted)
- [0010: PR で変えたモジュールにミューテーションテストをかけ、生き残りを PR にコメントする](./0010-mutation-testing-on-changed-modules.md) - 承認済み(accepted)
