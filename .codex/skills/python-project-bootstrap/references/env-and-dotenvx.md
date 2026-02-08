# `.env.*` と dotenvx 運用ガイド

## 基本方針

- 環境変数は `.env.development` と `.env.production` で分離する。
- 秘密情報は dotenvx で `encrypted:` 形式にしてリポジトリ管理する。
- 秘密鍵を含む `.env.keys` はコミットしない。

## 推奨ファイル

- `.env.development`: 開発環境の設定
- `.env.production`: 本番環境の設定
- `.env.example`: 共有用テンプレート（秘密値は空またはダミー）
- `.env.keys`: dotenvx の秘密鍵（`.gitignore` に追加）

## 初期テンプレート例

```dotenv
#/-------------------[DOTENV_PUBLIC_KEY]--------------------/
#/            public-key encryption for .env files          /
#/----------------------------------------------------------/
DOTENV_PUBLIC_KEY_DEVELOPMENT="<REPLACE_WITH_PUBLIC_KEY>"

APP_ENV="development"
LOG_LEVEL="INFO"

# 秘密情報は encrypted: 形式を使用
OPENAI_API_KEY="encrypted:<REPLACE_WITH_ENCRYPTED_VALUE>"
```

## よく使うコマンド

```bash
# dotenvx のセットアップ確認
dotenvx --version

# .env.production に暗号化して値を書き込む
dotenvx set OPENAI_API_KEY "sk-..." --encrypt -f .env.production

# 暗号化済み .env.production を使って実行
dotenvx run --env-file=.env.production -- uv run python -m your_package
```

## AGENTS.md への記載ルール

- どの実行モードがどの `.env.*` を使うかを明記する。
- `DOTENV_PUBLIC_KEY_<ENV>` を各 `.env.*` の先頭に置く。
- 共有時は「秘密鍵は配布しない」「公開鍵と暗号文のみコミットする」を明記する。

## チェックポイント

- `.env.keys` が `.gitignore` に入っている。
- `.env.example` に平文秘密情報が含まれていない。
- `dotenvx run --env-file=...` の実行例が README/AGENTS にある。
