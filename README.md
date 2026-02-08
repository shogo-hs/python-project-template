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

## 同梱Skill一覧（repoローカル正本）

テンプレートには以下の Skill を同梱している。運用時の正本は常に `<repo>/.codex/skills/` とする。

- `python-project-bootstrap`
- `python-uv-ci-setup`
- `task-design-gate`
- `api-spec-sync`
- `git-commit`

更新方針:

- global 側 Skill を更新した場合も、必要な差分はこのテンプレート側へ取り込み、PR でレビューしてから反映する。
- 参照のみを増やして実体を同梱しない運用は避ける（新規環境で参照切れを起こすため）。

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

## 新しいプロジェクトの立ち上げ手順

以下は「手順 1-3 は自分で実施し、手順 4 以降を任せる」運用を想定した最短フロー。

1. テンプレートから新規リポジトリを作成し、ローカルへ clone する。
2. `docs/ai/canonical/*.md` をプロジェクト方針に合わせて編集する。
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
- 共有 Skill は `<repo>/.codex/skills/` を正本としてコミット管理する。

## Symlink について

- 既定運用では symlink を使わない。
- 理由: OS/Git 設定差（例: `core.symlinks`）でチーム運用が不安定になりうるため。
- 必要な場合のみローカル実験として利用し、チーム標準は同期スクリプト方式を維持する。

## Codex + Cursor 併用ポリシー

- 新規作成は `.codex/skills` 同梱テンプレートリポジトリを優先する。
- 空リポジトリから開始するときだけ、グローバル `python-project-bootstrap` を初回1回だけ許容する。
- 初回生成後は `<repo>/.codex/skills/` を正本に固定する。
