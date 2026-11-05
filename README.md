# python-project-template

Codex と Claude Code で開発する Python プロジェクト向けのテンプレート。

- エージェント向けの規約は `AGENTS.md` 1 本。Codex はそのまま読み、Claude Code は `CLAUDE.md` の `@AGENTS.md` から読む。
- 手順書（スキル）は `.agents/skills/` 1 か所。Claude Code 用の `.claude/skills/` はそこへの symlink。
- 設計の正本はコード。設計判断の理由だけを `docs/adr/` に ADR として残す。
- 品質ゲートは uv + ruff + mypy + import-linter + deptry + pytest + pre-commit + GitHub Actions。

## 構成

```text
.
├── AGENTS.md                  # エージェント向けの規約（正本）
├── CLAUDE.md                  # @AGENTS.md の 1 行
├── .agents/skills/<name>/     # 手順書の正本（SKILL.md・references/・scripts/）
├── .claude/skills/<name>      # .agents/skills/<name> への symlink
├── docs/adr/                  # 設計判断の記録
└── docs/product/vision.md     # プロダクトの目的・対象ユーザー・成功状態
```

## 同梱の手順書

| 名前 | 使う場面 |
| --- | --- |
| `python-project-bootstrap` | 新しいプロジェクトを立ち上げる |
| `python-uv-ci-setup` | pyproject.toml・pre-commit・CI・Dependabot を整える |
| `adr-management` | 設計判断を ADR に記録・更新する |
| `git-commit` | 日本語の規約に沿ってコミットする |

どちらのエージェントも、依頼の内容から手順書を自動で選ぶ。Claude Code では `/python-project-bootstrap` のように名前でも呼べる。

## 新しいプロジェクトの立ち上げ

1. GitHub で「Use this template」から新規リポジトリを作り、clone する（Windows では `git config --global core.symlinks true` を先に設定する）。
2. リポジトリのルートで Codex か Claude Code を起動し、「プロジェクトを立ち上げて」と頼む。
3. エージェントの質問に答えて `docs/product/vision.md` を埋める。エージェントはパッケージの骨組み・`.env.example`・CI を作る。

## 環境変数

必要な変数は `.env.example` に並べてコミットし、実際の値は `.env`（コミットしない）に書く。読み込みは `uv run --env-file .env <コマンド>`。
