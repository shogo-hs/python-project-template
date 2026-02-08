# codex-cursor-python-template

Codex と Cursor を併用する Python プロジェクト向けのテンプレート。

## 目的

- AI 向け運用ルールの二重管理を防ぐ。
- `AGENTS.md`（Codex）と `.cursor/rules/*.mdc`（Cursor）を同じ正本から生成する。
- Skill 手順本文を `docs/ai/canonical/playbooks/` に集約し、Codex / Cursor の両方へ配布する。
- 共有 Skill と Playbook をリポジトリ同梱で管理し、チーム再現性を確保する。

## 構成

```text
.
├── AGENTS.md                     # 自動生成
├── .cursor/rules/*.mdc           # 自動生成
├── docs/ai/canonical/*.md        # 正本（手動編集）
├── docs/ai/canonical/playbooks/  # Skill手順の正本（手動編集）
├── docs/ai/playbooks/*.md        # 自動生成（共通配布先）
├── .codex/skills/*/SKILL.md      # 自動生成（Codex向け）
├── scripts/sync_ai_context.py    # 生成/検証
├── .codex/skills/*/references/   # 手順参照資料（手動編集）
├── .codex/skills/*/scripts/      # 補助スクリプト（手動編集）
└── .github/workflows/ai-context-sync.yml
```

## 同梱Skill一覧（手順は canonical 正本）

テンプレートには以下の Skill を同梱している。手順本文の正本は常に
`<repo>/docs/ai/canonical/playbooks/` とする。

- Codex 向け配布先: `<repo>/.codex/skills/*/SKILL.md`
- Cursor/Claude 向け配布先: `<repo>/docs/ai/playbooks/*.md` と `<repo>/.cursor/rules/20-playbooks.mdc`

- `python-project-bootstrap`
- `python-uv-ci-setup`
- `task-design-gate`
- `api-spec-sync`
- `git-commit`

更新方針:

- ルール本文は `docs/ai/canonical/playbooks/` のみを編集し、配布先は必ず同期スクリプトで再生成する。
- 参照のみを増やして実体を同梱しない運用は避ける（新規環境で参照切れを起こすため）。

## 運用ルール

1. ルール変更は `docs/ai/canonical/` と `docs/ai/canonical/playbooks/` だけを編集する。
2. `python3 scripts/sync_ai_context.py` を実行して生成物を更新する。
3. `python3 scripts/sync_ai_context.py --check` で drift がないことを確認する。
4. PR では CI の `AI Context Sync` チェックを必須にする。

## クイックスタート

```bash
python3 scripts/sync_ai_context.py
python3 scripts/sync_ai_context.py --check
```

## 新しいプロジェクトの立ち上げ手順

以下は「手順 1-3 は自分で実施し、手順 4 以降を任せる」運用を想定した最短フロー。

1. テンプレートから新規リポジトリを作成し、ローカルへ clone する。
2. `docs/ai/canonical/*.md` と `docs/ai/canonical/playbooks/*.md` をプロジェクト方針に合わせて編集する。
3. 反映確認を実行する。
   ```bash
   python3 scripts/sync_ai_context.py
   python3 scripts/sync_ai_context.py --check
   ```
4. 手順 4 以降をまとめて実行する。
   ```bash
   python3 scripts/bootstrap_after_canonical.py \
     --project-name "<project-name>" \
     --description "<project-description>" \
     --task-design-dir "docs/task-designs"
   ```

`bootstrap_after_canonical.py` は安全のため、`sync_ai_context.py` と `--check` を再実行してから
`python-project-bootstrap` を呼び出す。

### 立ち上げ直後に必ず行うこと（必須）

- CI 設定は必須。`$python-uv-ci-setup` を使って `.pre-commit-config.yaml` と `.github/workflows/ci.yml` を整備する。
- 手順正本は `<repo>/docs/ai/canonical/playbooks/` に固定し、配布先生成物をコミット管理する。

## Symlink について

- 既定運用では symlink を使わない。
- 理由: OS/Git 設定差（例: `core.symlinks`）でチーム運用が不安定になりうるため。
- 必要な場合のみローカル実験として利用し、チーム標準は同期スクリプト方式を維持する。

## Codex + Cursor 併用ポリシー

- 新規作成は `.codex/skills` 同梱テンプレートリポジトリを優先する。
- 空リポジトリから開始するときだけ、グローバル `python-project-bootstrap` を初回1回だけ許容する。
- 初回生成後は `docs/ai/canonical/playbooks/` を手順正本に固定し、`sync_ai_context.py` で Codex / Cursor へ配布する。
