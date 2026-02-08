# タスクルーティング

- 実装前設計: `$task-design-gate`
- Python の CI / 品質ゲート導入: `$python-uv-ci-setup`
- 新規プロジェクト初期構築: `$python-project-bootstrap`
- API 仕様同期: `$api-spec-sync`
- コミット実行: `$git-commit`

## 使い分けルール

- AGENTS.md には「いつどの Skill を使うか」だけを書く。
- 詳細手順の正本は `docs/ai/canonical/playbooks/*.md` に集約し、`scripts/sync_ai_context.py` で `docs/ai/playbooks/*.md` と `.codex/skills/*/SKILL.md` へ配布する。
- `references/` と `scripts/` は Skill ごとの補助資料として管理する。
- 同じ手順を AGENTS.md と Skill に重複記載しない。
