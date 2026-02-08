#!/usr/bin/env python3
"""canonical から AGENTS.md と Cursor rules を生成・検証する。"""

from __future__ import annotations

import argparse
from pathlib import Path

CANONICAL_FILES = {
    "global": Path("docs/ai/canonical/global-policies.md"),
    "routing": Path("docs/ai/canonical/task-routing.md"),
    "coding": Path("docs/ai/canonical/coding-standards.md"),
}

OUTPUT_FILES = {
    "agents": Path("AGENTS.md"),
    "cursor_global": Path(".cursor/rules/00-global.mdc"),
    "cursor_routing": Path(".cursor/rules/10-task-routing.mdc"),
}

AUTO_HEADER = (
    "<!-- AUTO-GENERATED FILE. DO NOT EDIT DIRECTLY. -->\n"
    "<!-- source: docs/ai/canonical/* + scripts/sync_ai_context.py -->\n"
)


def strip_first_heading(markdown: str) -> str:
    """先頭見出しを除去して本文だけを返す。"""
    lines = markdown.strip().splitlines()
    if lines and lines[0].startswith("#"):
        return "\n".join(lines[1:]).strip()
    return "\n".join(lines).strip()


def read_canonical(root: Path) -> dict[str, str]:
    """canonical ファイルを読み込む。"""
    contents: dict[str, str] = {}
    for key, rel_path in CANONICAL_FILES.items():
        path = root / rel_path
        if not path.exists():
            raise FileNotFoundError(f"missing canonical file: {path}")
        contents[key] = path.read_text(encoding="utf-8")
    return contents


def build_agents(canonical: dict[str, str]) -> str:
    """AGENTS.md の内容を生成する。"""
    global_body = strip_first_heading(canonical["global"])
    routing_body = strip_first_heading(canonical["routing"])
    coding_body = strip_first_heading(canonical["coding"])

    return (
        "# AGENTS.md\n\n"
        f"{AUTO_HEADER}\n"
        "## このファイルについて\n"
        "- このファイルは自動生成です。直接編集しないでください。\n"
        "- 変更は `docs/ai/canonical/` を編集し、`python3 scripts/sync_ai_context.py` を実行してください。\n\n"
        "## 1. グローバルポリシー\n"
        f"{global_body}\n\n"
        "## 2. タスクルーティング\n"
        f"{routing_body}\n\n"
        "## 3. コーディング標準\n"
        f"{coding_body}\n"
    )


def build_cursor_rule(description: str, body: str) -> str:
    """Cursor rule (.mdc) の内容を生成する。"""
    return (
        "---\n"
        f'description: "{description}"\n'
        "alwaysApply: true\n"
        "---\n\n"
        "<!-- AUTO-GENERATED FILE. DO NOT EDIT DIRECTLY. -->\n"
        "<!-- source: docs/ai/canonical/* + scripts/sync_ai_context.py -->\n\n"
        f"{body.strip()}\n"
    )


def build_outputs(canonical: dict[str, str]) -> dict[Path, str]:
    """出力ファイル群を生成する。"""
    global_body = strip_first_heading(canonical["global"])
    routing_body = strip_first_heading(canonical["routing"])
    coding_body = strip_first_heading(canonical["coding"])

    cursor_global = "# グローバルポリシー\n\n" + global_body + "\n\n# コーディング標準\n\n" + coding_body
    cursor_routing = "# タスクルーティング\n\n" + routing_body

    return {
        OUTPUT_FILES["agents"]: build_agents(canonical),
        OUTPUT_FILES["cursor_global"]: build_cursor_rule("プロジェクト共通ポリシーと標準", cursor_global),
        OUTPUT_FILES["cursor_routing"]: build_cursor_rule("タスク別のSkillルーティング", cursor_routing),
    }


def write_outputs(root: Path, outputs: dict[Path, str]) -> list[Path]:
    """出力を書き込み、変更されたファイル一覧を返す。"""
    changed: list[Path] = []
    for rel_path, content in outputs.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        normalized = content.rstrip() + "\n"
        if path.exists() and path.read_text(encoding="utf-8") == normalized:
            continue
        path.write_text(normalized, encoding="utf-8")
        changed.append(rel_path)
    return changed


def check_outputs(root: Path, outputs: dict[Path, str]) -> list[Path]:
    """期待値との差分があるファイル一覧を返す。"""
    drift: list[Path] = []
    for rel_path, content in outputs.items():
        path = root / rel_path
        expected = content.rstrip() + "\n"
        if not path.exists() or path.read_text(encoding="utf-8") != expected:
            drift.append(rel_path)
    return drift


def parse_args() -> argparse.Namespace:
    """CLI 引数を解析する。"""
    parser = argparse.ArgumentParser(description="AI context files synchronizer")
    parser.add_argument("--check", action="store_true", help="差分検知のみ実施して終了する")
    parser.add_argument(
        "--root",
        default=".",
        help="テンプレートリポジトリのルートパス（既定: カレントディレクトリ）",
    )
    return parser.parse_args()


def main() -> int:
    """メイン処理。"""
    args = parse_args()
    root = Path(args.root).resolve()
    canonical = read_canonical(root)
    outputs = build_outputs(canonical)

    if args.check:
        drift = check_outputs(root, outputs)
        if drift:
            print("[NG] Generated files are out of date:")
            for rel_path in drift:
                print(f"  - {rel_path}")
            print("Run: python3 scripts/sync_ai_context.py")
            return 1
        print("[OK] Generated files are up to date.")
        return 0

    changed = write_outputs(root, outputs)
    if changed:
        print("[OK] Updated generated files:")
        for rel_path in changed:
            print(f"  - {rel_path}")
    else:
        print("[OK] No changes needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
