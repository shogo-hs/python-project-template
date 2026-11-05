# ADR 0006: dotenvx をやめ、.env.example をコミットして .env はコミットしない

最終更新: 2026-11-05
- ステータス: 承認済み(accepted)
- 決定者: shogo-hs

## 1. 文脈

- これまでは `.env.development` / `.env.production` を dotenvx の `encrypted:` 形式でコミットし、復号鍵のファイルだけを除外していた。
- dotenvx の CLI の導入と鍵の受け渡しが必要で、新しく参加する人とエージェントの手順が増えていた。

## 2. 決定

- 必要な環境変数の名前とダミー値を `.env.example` に書いてコミットする。
- 実際の値は `.env` に書き、`.gitignore` で除外する（`.env`・`.env.*` を除外し、`!.env.example` で戻す）。
- 読み込みは `uv run --env-file .env <コマンド>` を使い、python-dotenv などの依存は足さない。
- 本番の値は実行環境（GitHub Actions の設定や、クラウドの管理サービスなど）から渡す。

## 3. 代替案と不採用理由

- 代替案A: dotenvx を続ける。
  - 不採用理由: 暗号化した値をリポジトリに置く利点より、CLI と鍵の運用の手間が大きい。

## 4. 影響

- 変数を足したら `.env.example` も同じコミットで更新する（AGENTS.md に記載）。

## 5. 変更履歴

- 2026-11-05: 新規作成
