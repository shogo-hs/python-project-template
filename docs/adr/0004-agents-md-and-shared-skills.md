# ADR 0004: AGENTS.md と .agents/skills を直接の正本にし、Cursor 対応と生成スクリプトをやめる

最終更新: 2026-11-05
- ステータス: 承認済み(accepted)
- 決定者: shogo-hs
- 関連: [ADR 0005](./0005-code-as-design-source-of-truth.md)

## 1. 文脈

- これまでは `docs/ai/canonical/` を正本とし、`scripts/sync_ai_context.py` で `AGENTS.md`・`CLAUDE.md`・`.cursor/rules/*.mdc`・`docs/ai/playbooks/*.md`・`.claude/skills/*/SKILL.md` を生成していた。
- Cursor は使わなくなった。Cursor を外すと、生成物は「3 ファイルを連結した AGENTS.md」と「手順書の同じ中身のコピー 2 組」だけになる。
- Codex はリポジトリの `AGENTS.md` と `.agents/skills/` を読む。Claude Code は `CLAUDE.md` と `.claude/skills/` を読む（`CLAUDE.md` が無いときだけ `AGENTS.md` を読む）。両者とも Agent Skills 標準の `SKILL.md` に準拠し、symlink のスキルフォルダを辿る。
- 生成スクリプトは不要になった生成物を消さず、`--check` でも検出しなかった。

## 2. 決定

- `AGENTS.md` を直接編集する正本にする。`CLAUDE.md` は `@AGENTS.md` の 1 行だけにする。
- 手順書は `.agents/skills/<name>/`（`SKILL.md`・`references/`・`scripts/`）を正本にし、`.claude/skills/<name>` をそこへの相対 symlink にする。
- `.cursor/`・`docs/ai/`・`scripts/sync_ai_context.py`・`scripts/bootstrap_after_canonical.py`・`.github/workflows/ai-context-sync.yml` を削除する。
- 以前 README で決めていた「symlink を使わない」方針はこれで置き換える。2026-11-05 に Claude Code 2.1.316 と codex-cli 0.160.0 で、symlink にしたスキルが読まれることを確認した。

## 3. 代替案と不採用理由

- 代替案A: 生成スクリプトを残し、Cursor の出力だけ外す。
  - 不採用理由: 残る生成は連結とコピーだけで、339 行のスクリプトと CI を持つ理由が無い。
- 代替案B: `CLAUDE.md` を置かず、Claude Code に `AGENTS.md` を直接読ませる。
  - 不採用理由: v2.1.277 より前の Claude Code や、Bedrock・Vertex 経由では読まれない。`@AGENTS.md` の 1 行なら確実に読める。
- 代替案C: スキルを `.claude/skills/` と `.agents/skills/` に二重に置く。
  - 不採用理由: 片方だけ直してずれる。

## 4. 影響

- Windows で clone する人は `core.symlinks=true` が必要（README に記載）。
- サブエージェントの定義は形式が違う（Claude Code は `.claude/agents/*.md`、Codex は `.codex/agents/*.toml`）ので、持つなら 2 本ずつ書く。

## 5. 変更履歴

- 2026-11-05: 新規作成
