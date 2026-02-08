# codex-cursor-python-template

Codex と Cursor を併用する Python プロジェクト向けのテンプレート。

## 目的

- AI 向け運用ルールの二重管理を防ぐ。
- `AGENTS.md`（Codex）と `.cursor/rules/*.mdc`（Cursor）を同じ正本から生成する。
- 手順本文を `docs/ai/canonical/playbooks/` に集約し、実行時は `docs/ai/playbooks/*.md` を参照する。
- 参照資料と補助スクリプトを repo 同梱で管理し、チーム再現性を確保する。

## 構成

```text
.
├── AGENTS.md                             # 自動生成
├── .cursor/rules/*.mdc                   # 自動生成
├── docs/ai/canonical/*.md                # 正本（手動編集）
├── docs/ai/canonical/playbooks/*.md      # Playbook手順の正本（手動編集）
├── docs/ai/playbooks/*.md                # 自動生成（実行時の参照先）
├── docs/ai/playbook-assets/**            # 参照資料（手動編集）
├── scripts/playbooks/**                  # 補助スクリプト（手動編集）
├── scripts/sync_ai_context.py            # 生成/検証
├── scripts/bootstrap_after_canonical.py  # 同期後ブートストラップ
└── .github/workflows/ai-context-sync.yml
```

## 同梱Playbook一覧

- `task-design-gate`
- `python-uv-ci-setup`
- `python-project-bootstrap`
- `api-spec-sync`
- `git-commit`

## 更新方針

- ルール本文は `docs/ai/canonical/` と `docs/ai/canonical/playbooks/` だけを編集する。
- `docs/ai/playbooks/*.md`、`AGENTS.md`、`.cursor/rules/*.mdc` は自動生成物として直接編集しない。
- Playbook の参照資料は `docs/ai/playbook-assets/`、補助スクリプトは `scripts/playbooks/` を正本とする。

## README と AGENTS の書き分け

| 書く場所 | 主な読者 | 記載する内容 | 記載しない内容 |
| --- | --- | --- | --- |
| `README.md` | 人間（開発者・利用者） | プロジェクト概要、構成、導入手順、運用導線 | エージェント向けの詳細実行規約 |
| `AGENTS.md` | AIエージェント | 実行時に守るルール、タスクルーティング、品質ゲート | 人向けの背景説明や長いオンボーディング解説 |

- エージェント向けの運用ルールを変更する場合は、`AGENTS.md` を直接編集せず `docs/ai/canonical/*.md` を更新して再生成する。
- ルーティングと実行手順は `AGENTS.md` から `docs/ai/playbooks/*.md` を参照する。

## 運用ルール

1. 必要な正本（canonical / playbook-assets / scripts/playbooks）を編集する。
2. `python3 scripts/sync_ai_context.py` を実行して生成物を更新する。
3. `python3 scripts/sync_ai_context.py --check` で drift がないことを確認する。
4. PR では CI の `AI Context Sync` チェックを必須にする。

## クイックスタート

```bash
python3 scripts/sync_ai_context.py
python3 scripts/sync_ai_context.py --check
```

## 新しいプロジェクトの立ち上げ手順

1. テンプレートから新規リポジトリを作成し、ローカルへ clone する。
2. `docs/ai/canonical/*.md` と `docs/ai/canonical/playbooks/*.md` をプロジェクト方針に合わせて編集する。
3. 反映確認を実行する。
   ```bash
   python3 scripts/sync_ai_context.py
   python3 scripts/sync_ai_context.py --check
   ```
4. 初期化をまとめて実行する。
   ```bash
   python3 scripts/bootstrap_after_canonical.py \
     --project-name "<project-name>" \
     --description "<project-description>" \
     --task-design-dir "docs/task-designs"
   ```

`bootstrap_after_canonical.py` は安全のため、`sync_ai_context.py` と `--check` を再実行してから
`python-project-bootstrap` 用の補助スクリプトを呼び出す。

### 立ち上げ直後に必ず行うこと（必須）

- CI 設定は必須。`python-uv-ci-setup` Playbook を使って `.pre-commit-config.yaml` と `.github/workflows/ci.yml` を整備する。
- 手順正本は `<repo>/docs/ai/canonical/playbooks/` に固定し、生成物をコミット管理する。

## Symlink について

- 既定運用では symlink を使わない。
- 理由: OS/Git 設定差（例: `core.symlinks`）でチーム運用が不安定になりうるため。
- 必要な場合のみローカル実験として利用し、チーム標準は同期スクリプト方式を維持する。

## Codex + Cursor 併用ポリシー

- 実行導線は `AGENTS.md` と `.cursor/rules/*.mdc` に統一する。
- 詳細手順は `docs/ai/playbooks/*.md` を共通参照先にする。
- 正本更新後は必ず `sync_ai_context.py` で再生成し、`--check` を通す。
