# AGENTS.md

Codex と Claude Code が共通で読むエージェント向けの規約（Claude Code は `CLAUDE.md` の `@AGENTS.md` から読む）。
人向けの入口は `README.md`。

## 基本方針

- ユーザーとのコミュニケーションは日本語で行う。
- 設計の正本はコード。設計判断の理由は `docs/adr/` の ADR にだけ残し、仕様書・API 文書・タスク設計書などコードと重複する文書は作らない。
- プロダクトの目的は `docs/product/vision.md` に書く。進捗は git の履歴と Issue で追う。
- ファイルを変える前に、変更の方針をユーザーに示して承認を取る。計画はリポジトリに保存しない。
- 想定外の大量差分、履歴を壊す操作、広範囲の削除が必要になったら作業を止めてユーザーに確認する。
- CI は必須とし、品質ゲートの失敗を残したままにしない。

## 手順書（スキル）

- 手順書は `.agents/skills/<name>/SKILL.md` が正本。`.claude/skills/<name>` はそこへの symlink で、Claude Code 用の入口。
- 手順書を足すときは `.agents/skills/<name>/` を作り、`ln -s ../../.agents/skills/<name> .claude/skills/<name>` で symlink を張る。
- 同じ手順を AGENTS.md と手順書に重複して書かない。AGENTS.md には常に守る規約だけを書く。

## 設計

- SOLID と DRY を基本原則にする。
- Hexagonal Architecture を採用し、`adapters` / `application` / `ports` / `domain` の責務を分ける。
- 依存方向は `adapters -> application -> ports -> domain` に固定し、domain は外部技術に依存しない。この依存方向は import-linter で検証する。

## Python

- Python 3.14 以上を前提にする。
- パッケージの追加・更新・削除は `uv add` / `uv remove` / `uv sync` を使い、`pip install` / `uv pip install` は使わない。
- 型ヒントを必須にし、`mypy` で検証する。
- `ruff` で format と lint をそろえる。
- docstring は Google style で、処理の意図が分かる説明を日本語で書く。1 行だけで終わらせず、引数があれば `Args`、戻り値があれば `Returns`、送出しうる例外があれば `Raises` を書く。
- docstring の説明を型ヒントと実装の挙動に矛盾させない。

## 環境変数と秘密情報

- 必要な環境変数は `.env.example` に名前とダミー値で並べてコミットする。変数を足したら `.env.example` も同じコミットで更新する。
- 実際の値は `.env` に書き、コミットしない（`.gitignore` 済み）。読み込みは `uv run --env-file .env <コマンド>`。
- API キー・トークン・秘密鍵・`.env` の中身は、出力・コミット・Issue・PR 本文に書かない。

## 文書の書き分け

- `README.md`: 人が最初に読む入口。目的・全体像・セットアップ・使い方を書く。
- `AGENTS.md`: エージェントが常に守る規約。手順の詳細は手順書に書く。
