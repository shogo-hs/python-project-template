#!/usr/bin/env python3
"""Python プロジェクトの初期構成を生成する。"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def normalize_package_name(name: str) -> str:
    """プロジェクト名から Python パッケージ名を生成する。"""
    candidate = re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower()
    if not candidate:
        candidate = "app"
    if candidate[0].isdigit():
        candidate = f"_{candidate}"
    return candidate


def detect_task_design_dir(target: Path, explicit: str | None) -> str:
    """既存構成に合わせてタスク設計ディレクトリを決める。"""
    if explicit:
        return explicit.strip("/")

    docs_task_designs = target / "docs" / "task-designs"
    docs_tasks = target / "docs" / "tasks"
    if docs_task_designs.exists() and not docs_tasks.exists():
        return "docs/task-designs"
    return "docs/tasks"


def write_text_file(path: Path, content: str, force: bool, report: dict[str, list[str]]) -> None:
    """ファイルを作成または更新し、結果を集計する。"""
    if path.exists():
        current = path.read_text(encoding="utf-8")
        if current == content:
            report["unchanged"].append(str(path))
            return
        if force:
            path.write_text(content, encoding="utf-8")
            report["updated"].append(str(path))
        else:
            report["skipped"].append(str(path))
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    report["created"].append(str(path))


def ensure_directories(paths: list[Path], report: dict[str, list[str]]) -> None:
    """必要なディレクトリ群を作成する。"""
    for path in paths:
        if path.exists():
            continue
        path.mkdir(parents=True, exist_ok=True)
        report["created_dirs"].append(str(path))


def ensure_gitignore(target: Path, report: dict[str, list[str]]) -> None:
    """推奨エントリを .gitignore に追加する。"""
    required_entries = [
        ".env.keys",
        ".venv/",
        "__pycache__/",
        ".pytest_cache/",
        ".mypy_cache/",
        ".ruff_cache/",
        ".worktrees/",
    ]
    gitignore_path = target / ".gitignore"
    if gitignore_path.exists():
        lines = gitignore_path.read_text(encoding="utf-8").splitlines()
    else:
        lines = []

    changed = False
    existing = set(lines)
    for entry in required_entries:
        if entry not in existing:
            lines.append(entry)
            changed = True

    if not gitignore_path.exists():
        gitignore_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        report["created"].append(str(gitignore_path))
    elif changed:
        gitignore_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        report["updated"].append(str(gitignore_path))
    else:
        report["unchanged"].append(str(gitignore_path))


def build_agents_md(
    project_name: str,
    description: str,
    python_version: str,
    task_design_dir: str,
) -> str:
    """AGENTS.md の初期テンプレートを返す。"""
    task_readme = f"{task_design_dir}/README.md"
    task_template = f"{task_design_dir}/_task-design-template.md"

    return f"""# AGENTS.md

## プロジェクト概要
- **名前**: {project_name}
- **説明**: {description}
- **ランタイム**:
  - backend: Python {python_version} (`uv` 管理)

## AIコーディング向けドキュメント
- 人向けの運用ガイドは `README.md` を参照する。
- 実装方針:
  - `docs/rules/solid/README.md`
  - `docs/rules/code_architecture/README.md`
- アーキテクチャ概要: `docs/architecture/hexagonal-architecture.md`
- タスク設計: `{task_readme}`
- タスク設計テンプレート: `{task_template}`
- APIテンプレート: `docs/api/_endpoint_template.md`
- API一覧: `docs/api/index.md`

## Task Design Gate (Mandatory)

- すべてのタスク依頼で、作業開始前に必ずタスク設計書を作成する（例外なし）。
- タスク設計書は `{task_design_dir}/` に保存する。ディレクトリが存在しない場合は作成する。
- ファイル名は `YYYYMMDDHHMMSS_{{task-name}}.md`（JST 初版作成日時）を使用する。
- `task-name` は英小文字の kebab-case を使用する。
- 設計書に未解消のオープン事項がある間は実装を開始しない。
- 実装ファイルの編集は、設計書に対するユーザーの明示承認後にのみ許可する。
- 実装中にスコープ変更が発生した場合、実装を停止して設計書を更新し、再承認を取得する。

## Skill運用ルール

- 既存スキルで対応できる場合は再利用を優先する。
- CI 設定は必須とし、`$python-uv-ci-setup` を利用して完了させる。
- API 仕様変更がある場合は `$api-spec-sync` を使って `docs/api/` と実装を同期する。
- 実装前の設計ゲートは `$task-design-gate` を利用する。
- コミット時は `$git-commit` を利用して規約を満たす。
- AGENTS.md には方針とルーティングのみ記載し、詳細手順は各 Skill に集約する。

## Skill配置方針（チーム再現性）
- 原則として新規作成は `.codex/skills` 同梱のテンプレートリポジトリから開始する。
- 空リポジトリから開始する場合のみ、グローバル `$python-project-bootstrap` を初回1回だけ使用する。
- 初回生成直後に共有 Skill を `<repo>/.codex/skills/` に配置してコミットし、以後は repo ローカルを正本にする。
- 個人ホーム配下の Skill は補助用途とし、必須依存にしない。
- 共有 Skill の更新は PR でレビューする。

## コードスタイル
- 共通:
  - 実装方針の基本として `docs/rules/solid/README.md` を参照する。
  - DRY 原則を守り、重複ロジックは責務に応じて層へ集約する。
- Python:
  - PEP 8 / 4 スペースインデント、型ヒント必須。
  - ログは標準の `logging` を利用し、モジュール単位でロガーを取得する。
  - 関数・メソッドには簡潔な **日本語** の docstring を記述する。

## 作業ルール
- 必ず作業後に、作業によって生じた変更と `README.md`, `AGENTS.md` の内容差分を確認し、差があれば更新すること。
- タスク依頼時はすぐにコードを書き始めず、まず `{task_design_dir}/` 配下にタスク設計ドキュメントを配置し、レビューを仰ぐこと。
- タスク実行時は適宜「実装タスクリスト」の進捗を更新しながら進めること。
- まとまった変更は小さなコミットに分割する。
- ランタイム設定や手順を変更したら本ファイルを更新すること。

## 環境変数 / シークレット運用
- 環境変数は `.env.development`, `.env.production` から取得する。
- 秘密情報は dotenvx で暗号化し、`encrypted:` 形式で管理する。
- `DOTENV_PUBLIC_KEY_DEVELOPMENT`, `DOTENV_PUBLIC_KEY_PRODUCTION` を利用する。
- `.env.keys` は秘密鍵を含むためコミットしない。

## CI / 品質ゲート
- CI 設定は必須。`$python-uv-ci-setup` で `.pre-commit-config.yaml` と `.github/workflows/ci.yml` を整備する。
- 実行コマンドや失敗時の復旧手順は `python-uv-ci-setup` Skill の記述を正本とする。

## Git戦略: Git Worktree ワークフロー
- ルートディレクトリで `git switch` や `git checkout` によるブランチ切り替えは禁止。
- タスクごとに `.worktrees/<branch-name>/` を作成して作業する。

### 新規タスク着手時の手順
1. `.worktrees/` が存在するか確認し、`.gitignore` に追加されていることを確認する。
2. 新しいタスク開始時に worktree を作成する。
   ```bash
   git worktree add .worktrees/feat/<task-name> -b feat/<task-name>
   ```
3. 必ず `.worktrees/<branch-name>/` 以下を編集対象にする。
4. マージ後は不要 worktree を削除する。
   ```bash
   git worktree remove .worktrees/<branch-name>
   git worktree prune
   ```

## Git コミットメッセージ
**重要: すべてのコミットメッセージは日本語で記述すること。**

- 必ずプレフィックスを使用する (`feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`)
- プレフィックスを含めて 50 文字以内
- 現在形（辞書形）または体言止めを使用する
- 末尾に句点（。）を付けない
- 形式: `prefix: メッセージ`

## コミュニケーション
- ユーザーとエージェント間の連絡は日本語で行うこと。
"""


def build_solid_rules() -> str:
    """SOLID/DRY ガイドを返す。"""
    return """# SOLID / DRY ガイドライン

## 目的

設計品質を一定に保つため、SOLID 原則と DRY 原則を実装判断の基準として採用する。

## SOLID

### S: Single Responsibility Principle
- 1 つのモジュールは 1 つの責務のみを持つ。
- 変更理由が複数になる実装は分割する。

### O: Open/Closed Principle
- 既存コードの破壊的変更ではなく、拡張で要件に対応する。
- 条件分岐の増殖より抽象化と差し替えを優先する。

### L: Liskov Substitution Principle
- 置換可能性を壊す継承・実装を禁止する。
- 契約を破る例外仕様や戻り値変更を避ける。

### I: Interface Segregation Principle
- 大きすぎるインターフェースを避ける。
- 利用側が必要な最小契約に分割する。

### D: Dependency Inversion Principle
- 上位層は実装ではなく抽象に依存する。
- 外部 I/O には ports を介して接続する。

## DRY

- 同一ルールが複数箇所に出現する場合は共通化する。
- ただし誤った早期抽象化は避け、責務境界が明確な共通化のみ採用する。

## 運用チェック

- 重複したバリデーションが複数 adapter に存在しないか。
- use case に技術詳細が混入していないか。
- テストしづらい密結合が発生していないか。
"""


def build_code_architecture_rules(package_name: str) -> str:
    """アーキテクチャガイドを返す。"""
    return f"""# コードアーキテクチャ方針

## 採用アーキテクチャ

本プロジェクトは Hexagonal Architecture（Ports and Adapters）を採用する。

## 依存方向

- `src/{package_name}/adapters` -> `src/{package_name}/application`
- `src/{package_name}/application` -> `src/{package_name}/domain`
- `src/{package_name}/ports` は契約のみを保持し、実装は持たない。
- `domain` は外部ライブラリ・フレームワークへ依存しない。

## 層責務

- `domain`: エンティティ、値オブジェクト、ドメインサービス
- `application`: ユースケース、トランザクション境界、アプリケーションサービス
- `ports`: 入出力契約（抽象）
- `adapters`: Web/API/DB/外部サービス連携の実装

## 禁止事項

- domain 層で DB クエリや HTTP 呼び出しを行う。
- adapter 層へビジネスルールを複製する。
- use case で framework 依存型を直接受け取る。
"""


def build_hexagonal_architecture_doc(package_name: str) -> str:
    """Hexagonal 概要ドキュメントを返す。"""
    return f"""# Hexagonal Architecture

## ディレクトリ構成

```text
src/{package_name}/
  adapters/
    inbound/
    outbound/
  application/
    use_cases/
    services/
  domain/
    entities/
    value_objects/
    services/
  ports/
    inbound/
    outbound/
```

## 開発ガイド

1. まず `domain` でビジネスルールを定義する。
2. `application` でユースケースを実装する。
3. 外部 I/O は `ports` に契約を定義する。
4. `adapters` で `ports` の実装を提供する。

## テスト戦略

- 単体テストは `domain` と `application` を中心に行う。
- 結合テストは adapter + 外部依存の接続点を検証する。
- port 契約を満たすことをインターフェーステストで確認する。
"""


def build_task_readme(task_design_dir: str) -> str:
    """タスク設計ディレクトリ README を返す。"""
    return f"""# タスク設計書の保存先

このディレクトリにタスク設計書を保存する。

- 全タスク依頼で、作業開始前にタスク設計書の作成を必須とする。
- 保存先: `{task_design_dir}/`
- 命名規則: `YYYYMMDDHHMMSS_{{task-name}}.md`
- 時刻: 初版作成日時（JST）
- `task-name`: 英小文字の kebab-case
- 更新時: 原則ファイル名を変更しない
"""


def build_task_template() -> str:
    """タスク設計テンプレートを返す。"""
    return """# タスク設計書: <タイトル>

最終更新: <YYYY-MM-DD>
- ステータス: <下書き(draft) / レビュー待ち(review-ready) / 承認済み(approved) / 保留(blocked) / 実装中(in-progress) / 完了(done)>
- 作成者: <名前>
- レビュー: <担当者>
- 対象コンポーネント: <backend / frontend / docs / infra / data>
- 関連: <リンクや関連設計書>
- チケット/リンク: <Issue/PR/外部リンク>

## 0. TL;DR
- <目的と結論を3〜5行で要約>

## 1. 背景 / 課題
- <なぜこの変更が必要か>

## 2. ゴール / 非ゴール
### 2.1 ゴール
- <達成したい状態>

### 2.2 非ゴール
- <今回やらないこと>

## 3. スコープ / 影響範囲
- 変更対象: <API/画面/データ/設定など>
- 影響範囲: <利用者/運用/データなど>
- 互換性: <後方互換/破壊的変更の有無>
- 依存関係: <外部API/ライブラリ/他チーム依存>

## 4. 要件
### 4.1 機能要件
- <機能要件>

### 4.2 非機能要件 / 制約
- <性能/可用性/セキュリティ/運用制約>

## 5. 仕様 / 設計
### 5.1 全体方針
- <設計方針>

### 5.2 変更点一覧
| 対象 | 変更内容 | 影響 | 備考 |
| --- | --- | --- | --- |
| <component / file / API> | <何を変えるか> | <影響> | <補足> |

## 6. テスト計画
- 単体: <対象>
- 結合: <対象>
- 手動: <手順>
- 合格条件: <何をもって完了とするか>

## 7. 受け入れ基準
- <操作手順と期待結果>

## 8. リスク / 対策
- <リスクと回避策>

## 9. オープン事項 / 要確認
- <未確定事項>
- ※未解消事項がある場合、実装を開始しない。

## 10. 実装タスクリスト
- [ ] <実装タスク>
- [ ] <テスト追加>
- [ ] <運用作業>

## 11. ドキュメント更新
- [ ] `README.md`（必要に応じて）
- [ ] `AGENTS.md`（必要に応じて）
- [ ] `docs/`（該当ファイルあれば）

## 12. 承認ログ
- 承認者: <名前>
- 承認日時: <YYYY-MM-DD HH:mm>
- 承認コメント: <条件付き承認なら条件を明記>

## 実装開始条件
- [ ] ステータスが `承認済み(approved)` である
- [ ] 9. オープン事項が空である
- [ ] 受け入れ基準とテスト計画に合意済み
"""


def build_api_index() -> str:
    """API index テンプレートを返す。"""
    return """# API 一覧

このドキュメントは API 仕様の一覧を管理する。

## ルール

- 1 エンドポイント 1 ファイルで管理する。
- 仕様変更時は必ず index と個別ファイルを同時更新する。
- 実装との差分がない状態を維持する。

## エンドポイント

| ID | Method | Path | Summary | Spec |
| --- | --- | --- | --- | --- |
| sample-health | GET | /health | ヘルスチェック | `docs/api/sample-health.md` |
"""


def build_api_endpoint_template() -> str:
    """API エンドポイントテンプレートを返す。"""
    return """# <endpoint-id>

## 概要
- Method: `<GET|POST|PUT|PATCH|DELETE>`
- Path: `</path>`
- 認証: `<required|optional|none>`

## リクエスト

### Path Parameters
| name | type | required | description |
| --- | --- | --- | --- |

### Query Parameters
| name | type | required | description |
| --- | --- | --- | --- |

### Body
```json
{}
```

## レスポンス

### 2xx
```json
{}
```

### 4xx/5xx
```json
{{
  "error": "<code>",
  "message": "<human-readable>"
}}
```

## 備考
- 実装と差分がないことを確認する。
"""


def build_env_file(environment: str) -> str:
    """環境別 .env テンプレートを返す。"""
    suffix = environment.upper()
    return f"""#/-------------------[DOTENV_PUBLIC_KEY]--------------------/
#/            public-key encryption for .env files          /
#/----------------------------------------------------------/
DOTENV_PUBLIC_KEY_{suffix}="<REPLACE_WITH_PUBLIC_KEY>"

APP_ENV="{environment}"
LOG_LEVEL="INFO"

# --- 設定値 (平文) ---
DATABASE_URL="postgresql://app:app@localhost:5432/app"

# --- 秘密情報 (暗号化) ---
OPENAI_API_KEY="encrypted:<REPLACE_WITH_ENCRYPTED_VALUE>"
"""


def build_env_example() -> str:
    """.env.example テンプレートを返す。"""
    return """APP_ENV="development"
LOG_LEVEL="INFO"
DATABASE_URL="postgresql://app:app@localhost:5432/app"
OPENAI_API_KEY=""
"""


def parse_args() -> argparse.Namespace:
    """CLI 引数を解析する。"""
    parser = argparse.ArgumentParser(description="Python プロジェクト初期構成を生成する")
    parser.add_argument("--target", default=".", help="生成先ルートディレクトリ")
    parser.add_argument("--project-name", required=True, help="プロジェクト名")
    parser.add_argument("--description", default="<TBD>", help="プロジェクト説明")
    parser.add_argument("--package-name", help="Python パッケージ名")
    parser.add_argument("--python-version", default="3.12+", help="Python バージョン表記")
    parser.add_argument(
        "--task-design-dir",
        help="タスク設計ディレクトリ（例: docs/tasks または docs/task-designs）",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="既存ファイルを上書きする",
    )
    return parser.parse_args()


def main() -> None:
    """メイン処理。"""
    args = parse_args()
    target = Path(args.target).resolve()
    package_name = args.package_name or normalize_package_name(args.project_name)
    task_design_dir = detect_task_design_dir(target, args.task_design_dir)

    report: dict[str, list[str]] = {
        "created_dirs": [],
        "created": [],
        "updated": [],
        "skipped": [],
        "unchanged": [],
    }

    directories = [
        target / "src" / package_name / "adapters" / "inbound",
        target / "src" / package_name / "adapters" / "outbound",
        target / "src" / package_name / "application" / "use_cases",
        target / "src" / package_name / "application" / "services",
        target / "src" / package_name / "domain" / "entities",
        target / "src" / package_name / "domain" / "value_objects",
        target / "src" / package_name / "domain" / "services",
        target / "src" / package_name / "ports" / "inbound",
        target / "src" / package_name / "ports" / "outbound",
        target / "tests" / "unit",
        target / "tests" / "integration",
        target / "docs" / "rules" / "solid",
        target / "docs" / "rules" / "code_architecture",
        target / "docs" / "architecture",
        target / "docs" / "api",
        target / Path(task_design_dir),
    ]
    ensure_directories(directories, report)

    files = {
        target / "AGENTS.md": build_agents_md(
            project_name=args.project_name,
            description=args.description,
            python_version=args.python_version,
            task_design_dir=task_design_dir,
        ),
        target / "docs" / "rules" / "solid" / "README.md": build_solid_rules(),
        target / "docs" / "rules" / "code_architecture" / "README.md": build_code_architecture_rules(package_name),
        target / "docs" / "architecture" / "hexagonal-architecture.md": build_hexagonal_architecture_doc(package_name),
        target / Path(task_design_dir) / "README.md": build_task_readme(task_design_dir),
        target / Path(task_design_dir) / "_task-design-template.md": build_task_template(),
        target / "docs" / "api" / "index.md": build_api_index(),
        target / "docs" / "api" / "_endpoint_template.md": build_api_endpoint_template(),
        target / ".env.development": build_env_file("development"),
        target / ".env.production": build_env_file("production"),
        target / ".env.example": build_env_example(),
    }

    for path, content in files.items():
        write_text_file(path, content, force=args.force, report=report)

    ensure_gitignore(target, report)

    print(f"Target: {target}")
    print(f"Package: {package_name}")
    print(f"Task design dir: {task_design_dir}")
    print("")

    for key in ["created_dirs", "created", "updated", "skipped", "unchanged"]:
        items = report[key]
        print(f"{key}: {len(items)}")
        for item in items:
            print(f"  - {item}")


if __name__ == "__main__":
    main()
