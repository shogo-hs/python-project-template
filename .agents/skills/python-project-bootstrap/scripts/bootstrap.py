#!/usr/bin/env python3
"""Hexagonal 構成のパッケージ骨組み・smoke テスト・.env.example を生成する。

既存のファイルは上書きしない。何度実行しても結果は同じになる。
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

LAYER_DIRS = [
    "adapters/inbound",
    "adapters/outbound",
    "application/use_cases",
    "application/services",
    "domain/entities",
    "domain/value_objects",
    "domain/services",
    "ports/inbound",
    "ports/outbound",
]
TEST_DIRS = ["unit", "integration"]
GITIGNORE_ENTRIES = [".env", ".env.*", "!.env.example", ".worktrees/"]
ENV_EXAMPLE = """# 必要な環境変数の一覧。値はダミー。実際の値は .env に書く（コミットしない）。
# 読み込み: uv run --env-file .env <コマンド>
APP_ENV=development
LOG_LEVEL=INFO
"""


def normalize_package_name(name: str) -> str:
    """プロジェクト名から Python のパッケージ名を作る。

    Args:
        name: プロジェクト名（例: `my-app`）。

    Returns:
        snake_case のパッケージ名（例: `my_app`）。先頭が数字なら `_` を付ける。
    """
    candidate = re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower() or "app"
    return f"_{candidate}" if candidate[0].isdigit() else candidate


def build_smoke_test(package_name: str) -> str:
    """パッケージが import できることを確かめる smoke テストを返す。

    生成直後でも pytest が「テスト 0 件」で失敗しないようにする。

    Args:
        package_name: `src/` 配下のパッケージ名。

    Returns:
        `tests/unit/test_smoke.py` の内容。
    """
    return f'''"""パッケージが import できることを確かめる smoke テスト。"""

import importlib


def test_package_is_importable() -> None:
    """パッケージを import でき、モジュールが返ることを確かめる。"""
    assert importlib.import_module("{package_name}")
'''


def planned_files(target: Path, package_name: str) -> dict[Path, str]:
    """生成するファイルのパスと内容を返す。

    `src/<package>` と `tests` の配下はすべて `__init__.py` を置いてパッケージにする。
    無いと import-linter が層を見つけられず、mypy と pytest も解決できない。

    Args:
        target: 生成先のルートディレクトリ。
        package_name: `src/` 配下のパッケージ名。

    Returns:
        パスから内容への対応。
    """
    package_root = target / "src" / package_name
    tests_root = target / "tests"
    leaves = [package_root / d for d in LAYER_DIRS] + [tests_root / d for d in TEST_DIRS]
    package_dirs = {package_root, tests_root}
    for leaf in leaves:
        for root in (package_root, tests_root):
            if leaf.is_relative_to(root):
                package_dirs.update(p for p in [leaf, *leaf.parents] if p.is_relative_to(root))

    files = {d / "__init__.py": "" for d in sorted(package_dirs)}
    files[tests_root / "unit" / "test_smoke.py"] = build_smoke_test(package_name)
    files[target / ".env.example"] = ENV_EXAMPLE
    return files


def ensure_gitignore(target: Path) -> list[str]:
    """`.gitignore` に足りない行を末尾に足す。

    Args:
        target: 生成先のルートディレクトリ。

    Returns:
        追加した行。
    """
    path = target / ".gitignore"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    existing = set(text.splitlines())
    added = [e for e in GITIGNORE_ENTRIES if e not in existing]
    if added:
        prefix = text if not text or text.endswith("\n") else text + "\n"
        path.write_text(prefix + "\n".join(added) + "\n", encoding="utf-8")
    return added


def main() -> int:
    """引数を読み、骨組みを生成して結果を表示する。

    Returns:
        終了コード（常に 0）。
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".", help="生成先のルートディレクトリ")
    parser.add_argument("--project-name", required=True, help="プロジェクト名")
    parser.add_argument("--package-name", help="パッケージ名（既定: プロジェクト名の snake_case）")
    args = parser.parse_args()

    target = Path(args.target).resolve()
    package_name = args.package_name or normalize_package_name(args.project_name)

    for path, content in planned_files(target, package_name).items():
        if path.exists():
            print(f"skip    {path.relative_to(target)}")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"create  {path.relative_to(target)}")
    for entry in ensure_gitignore(target):
        print(f"ignore  {entry}")
    print(f"package: {package_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
