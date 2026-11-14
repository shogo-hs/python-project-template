# ADR 一覧

このプロジェクトの設計判断の記録（Architecture Decision Record）。書き方は `.agents/skills/adr-management/SKILL.md`。

## 決まり

- 形式は `NNNN-short-title.md`（4 桁の連番）。1 本に 1 つの判断だけを書く。
- ステータスは `提案(proposed)` / `承認済み(accepted)` / `却下(rejected)` / `置換済み(superseded)`。
- 既存の判断を置き換えるときは、新しい ADR を足し、新旧の双方にリンクを張る。書いた ADR の本文は書き換えない。
- テンプレートから引き継いだ決まり（ADR 0002）の理由は、テンプレートの `docs/adr/` にある。本文では「テンプレート ADR 000N」と呼び、このプロジェクトの ADR 番号と区別する。テンプレートの決まりを外すときは、「テンプレート ADR 000N を採らない」という ADR を足す。

## 一覧

- [0001: ADR で設計判断を記録する](./0001-record-architecture-decisions.md) - 承認済み(accepted)
- [0002: テンプレートの設計の決まりを引き継ぐ](./0002-adopt-template-baseline.md) - 承認済み(accepted)
