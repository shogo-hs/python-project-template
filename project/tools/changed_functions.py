"""2 つの版の `src/` を比べ、中身の変わった関数・メソッドを mutmut の名前で出す。

CI の `mutation` ジョブが、PR で変えた関数にだけ変異を入れるのに使う。
見るのは mutmut が変異を入れる範囲と同じで、モジュール直下の関数と、モジュール直下のクラスのメソッド
（関数の中の関数は外側の関数の一部として比べる。クラスの中のクラスと `if` / `try` の中の定義は見ない）。
構文木で比べるので、コメント・空行・整形だけの変更と、行がずれただけの関数は出ない。
引数・デコレーター・docstring の変更は出る。

使い方:
    python tools/changed_functions.py --base ../base/src --head src
"""

import argparse
import ast
import sys
from pathlib import Path

_FUNC = ast.FunctionDef | ast.AsyncFunctionDef


def functions(path: Path) -> dict[str, str]:
    """1 つのファイルの関数・メソッドを読む。

    Args:
        path: `.py` ファイル。無い・構文エラーで読めないときは、関数が 1 つも無いものとして扱う。

    Returns:
        mutmut の名前（`x_<関数>` か `xǁ<クラス>ǁ<メソッド>`）から、その定義の構文木の文字列への対応。
    """
    try:
        tree = ast.parse(path.read_bytes())
    except (SyntaxError, ValueError, OSError):
        return {}
    found: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, _FUNC):
            found[f"x_{node.name}"] = ast.dump(node)
        elif isinstance(node, ast.ClassDef):
            for method in node.body:
                if isinstance(method, _FUNC):
                    found[f"xǁ{node.name}ǁ{method.name}"] = ast.dump(method)
    return found


def changed(base: Path, head: Path) -> list[str]:
    """`head` にあって、`base` に無いか中身が違う関数・メソッドを並べる。

    Args:
        base: 変更前の `src/`。無ければ、すべての関数が増えたものとして扱う。
        head: 変更後の `src/`。

    Returns:
        `<モジュール>.x_<関数>` か `<モジュール>.xǁ<クラス>ǁ<メソッド>` の形の名前。
        後ろに `__mutmut_*` を付けると、その関数の変異だけに合うパターンになる。
    """
    names: list[str] = []
    for path in sorted(head.rglob("*.py")):
        rel = path.relative_to(head)
        module = ".".join(rel.with_suffix("").parts).removesuffix(".__init__")
        old = functions(base / rel)
        names += [
            f"{module}.{key}" for key, dump in functions(path).items() if old.get(key) != dump
        ]
    return names


def main(argv: list[str] | None = None) -> int:
    """コマンドラインから呼び、変わった関数の名前を 1 行に 1 つずつ標準出力に書く。

    Args:
        argv: コマンドライン引数。`None` なら `sys.argv` を使う。

    Returns:
        終了コード（常に 0）。
    """
    parser = argparse.ArgumentParser(
        description="2 つの版の src から、中身の変わった関数を mutmut の名前で出す。"
    )
    parser.add_argument("--base", type=Path, required=True, help="変更前の src ディレクトリ")
    parser.add_argument("--head", type=Path, required=True, help="変更後の src ディレクトリ")
    args = parser.parse_args(argv)
    sys.stdout.writelines(f"{name}\n" for name in changed(args.base, args.head))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
