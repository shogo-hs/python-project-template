# codex-cursor-python-template

Codex と Cursor を併用する Python プロジェクト向けのテンプレート。

## 目的

- AI 向け運用ルールの二重管理を防ぐ。
- `AGENTS.md`（Codex）と `.cursor/rules/*.mdc`（Cursor）を同じ正本から生成する。
- 共有 Skill をリポジトリ同梱で管理し、チーム再現性を確保する。

## 構成

```text
.
├── AGENTS.md                     # 自動生成
├── .cursor/rules/*.mdc           # 自動生成
├── docs/ai/canonical/*.md        # 正本（手動編集）
├── scripts/sync_ai_context.py    # 生成/検証
├── .codex/skills/                # 共有Skill
└── .github/workflows/ai-context-sync.yml
```

## 運用ルール

1. ルール変更は `docs/ai/canonical/` だけを編集する。
2. `python3 scripts/sync_ai_context.py` を実行して生成物を更新する。
3. `python3 scripts/sync_ai_context.py --check` で drift がないことを確認する。
4. PR では CI の `AI Context Sync` チェックを必須にする。

## クイックスタート

```bash
python3 scripts/sync_ai_context.py
python3 scripts/sync_ai_context.py --check
```

## Symlink について

- 既定運用では symlink を使わない。
- 理由: OS/Git 設定差（例: `core.symlinks`）でチーム運用が不安定になりうるため。
- 必要な場合のみローカル実験として利用し、チーム標準は同期スクリプト方式を維持する。

## Codex + Cursor 併用ポリシー

- 新規作成は `.codex/skills` 同梱テンプレートリポジトリを優先する。
- 空リポジトリから開始するときだけ、グローバル `python-project-bootstrap` を初回1回だけ許容する。
- 初回生成後は `<repo>/.codex/skills/` を正本に固定する。
