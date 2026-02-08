# コーディング標準

## 設計

- SOLID と DRY を基本原則にする。
- Hexagonal Architecture を採用し、`adapters/application/domain/ports` の責務を分離する。
- 依存方向は外側から内側へ固定し、domain は外部技術へ依存しない。

## Python

- Python 3.12+ を前提にする。
- 型ヒントを必須にし、`mypy` で検証する。
- `ruff` で format/lint を統一する。
- docstring は日本語で簡潔に書く。

## 環境変数

- `.env.development` / `.env.production` を利用する。
- 秘密情報は dotenvx の `encrypted:` 形式で管理する。
- `.env.keys` はコミットしない。
