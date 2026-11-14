"""Python のコードから関係グラフを作り、2 つの版の差分をレビュー用の Markdown にする。

CI が PR ごとに base と head の `src/` から毎回作り直すので、グラフは保存も手入力もしない。
モジュール直下とクラス直下の定義（`if` / `try` / `with` の中を含む）と、すべての import を構文から読む。
呼び出しは名前で解決する近似で、変数や辞書に入れた関数、`from x import *` で入れた名前、
関数の中で定義した関数は取れない。同じ名前のモジュール（`x.py`）とパッケージ（`x/`）が並ぶと、
定義の場所を取り違えることがある。

使い方:
    python tools/code_graph.py --base ../base/src --head src > code-graph.md
"""

import argparse
import ast
import re
import sys
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path

MARKER = "<!-- code-graph-diff -->"
MAX_ITEMS = 50
MAX_SIGNATURE = 200
MAX_COMMENT = 60_000  # GitHub のコメントの上限は 65,536 字
_DEF = ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef
_BLOCKS = ast.If | ast.Try | ast.TryStar | ast.With | ast.AsyncWith


@dataclass(frozen=True)
class Definition:
    """クラス・関数・メソッドの定義 1 つ。

    Attributes:
        qualname: `パッケージ.モジュール.名前` の形の完全な名前。
        module: 定義があるモジュールの名前。
        kind: `class` か `function`。
        path: 定義があるファイルの、`src/` からの相対パス。
        line: 定義の開始行。
        signature: 関数なら async かどうか・引数・戻り値の型、クラスなら継承元。変わったかを比べるのに使う。
    """

    qualname: str
    module: str
    kind: str
    path: str
    line: int
    signature: str


@dataclass
class Graph:
    """1 つの版のコードの関係。

    Attributes:
        definitions: 完全な名前から定義への対応。
        imports: プロジェクト内のモジュールどうしの import（import する側, される側）。
        calls: モジュールをまたぐ呼び出しと継承（呼ぶ側の定義, 呼ばれる側の定義）。
        unreadable: 構文エラーなどで読めなかったファイルの、`src/` からの相対パス。
    """

    definitions: dict[str, Definition] = field(default_factory=dict)
    imports: set[tuple[str, str]] = field(default_factory=set)
    calls: set[tuple[str, str]] = field(default_factory=set)
    unreadable: list[str] = field(default_factory=list)


def module_name(src: Path, path: Path) -> str:
    """ファイルのパスをモジュール名に直す。

    Args:
        src: パッケージを置いたディレクトリ（例 `src/`）。
        path: `src` の下の `.py` ファイル。

    Returns:
        `pkg.sub.mod` の形のモジュール名。`__init__.py` はパッケージ名になる。
    """
    parts = list(path.relative_to(src).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _statements(body: list[ast.stmt]) -> Iterator[ast.stmt]:
    """文の並びを、`if` / `try` / `with` の中まで平らにして返す（関数とクラスの中には入らない）。"""
    for node in body:
        if isinstance(node, _BLOCKS):
            for part in ("body", "orelse", "finalbody"):
                yield from _statements(getattr(node, part, []))
            for handler in getattr(node, "handlers", []):
                yield from _statements(handler.body)
        else:
            yield node


def _resolve_from(module: str, node: ast.ImportFrom, is_package: bool) -> str:
    """`from ... import` の対象のモジュール名を、相対 import も含めて絶対名にする。"""
    if not node.level:
        return node.module or ""
    package = module.split(".") if is_package else module.split(".")[:-1]
    base = package[: len(package) - node.level + 1]
    return ".".join([*base, node.module] if node.module else base)


def _imports(
    module: str, nodes: Iterable[ast.stmt], is_package: bool
) -> tuple[dict[str, str], list[str]]:
    """モジュールの import 文を読み、使えるようになった名前と import した先を返す。

    Args:
        module: 読んでいるモジュールの名前。
        nodes: 読む文。import 文以外は無視する。
        is_package: `__init__.py` なら True（相対 import の起点が自分自身になる）。

    Returns:
        （import で使えるようになった名前 → 指す先の完全な名前, import した先の完全な名前の一覧）。
    """
    names: dict[str, str] = {}
    targets: list[str] = []
    for node in nodes:
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                names[alias.asname or top] = alias.name if alias.asname else top
                targets.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            base = _resolve_from(module, node, is_package)
            for alias in node.names:
                if alias.name == "*":
                    targets.append(base)
                    continue
                names[alias.asname or alias.name] = f"{base}.{alias.name}"
                targets.append(f"{base}.{alias.name}")
    return names, targets


def _arg_names(node: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    """関数の引数の名前を集める（import した名前より引数が優先されるため）。"""
    a = node.args
    every = [*a.posonlyargs, *a.args, *a.kwonlyargs, *(x for x in (a.vararg, a.kwarg) if x)]
    return {x.arg for x in every}


def _dotted(expr: ast.expr) -> list[str] | None:
    """`a.b.c` の形の式を `["a", "b", "c"]` にする。それ以外の式なら None。"""
    if isinstance(expr, ast.Name):
        return [expr.id]
    if isinstance(expr, ast.Attribute):
        head = _dotted(expr.value)
        return [*head, expr.attr] if head else None
    return None


def _target(expr: ast.expr, names: dict[str, str], cls: str | None) -> str | None:
    """呼び出しや継承元の式から、指している定義の完全な名前を名前だけで推定する。"""
    parts = _dotted(expr)
    if not parts:
        return None
    if parts[0] == "self" and cls and len(parts) == 2:
        return f"{cls}.{parts[1]}"
    base = names.get(parts[0])
    return ".".join([base, *parts[1:]]) if base else None


def _signature(node: ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """定義の外から見える形（クラスなら継承元、関数なら async・引数・戻り値）を文字列にする。"""
    if isinstance(node, ast.ClassDef):
        return "(" + ", ".join(ast.unparse(b) for b in node.bases) + ")"
    prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
    returns = f" -> {ast.unparse(node.returns)}" if node.returns else ""
    return f"{prefix}({ast.unparse(node.args)}){returns}"


@dataclass
class _Module:
    """1 つのモジュールを読んだ結果（定義・名前の対応・未解決の参照）。"""

    name: str
    names: dict[str, str]
    is_package: bool
    targets: list[str] = field(default_factory=list)
    definitions: list[Definition] = field(default_factory=list)
    refs: set[tuple[str, str]] = field(default_factory=set)

    def visit(self, node: ast.stmt, parent: str, rel_path: str, cls: str | None = None) -> None:
        """定義 1 つを記録し、クラスなら中のメソッドへ、関数なら中の呼び出しへ進む。

        Args:
            node: 文。クラスか関数の定義でなければ何もしない。
            parent: 外側のクラスかモジュールの完全な名前。
            rel_path: このモジュールのファイルの、`src/` からの相対パス。
            cls: メソッドを見ているときの、そのクラスの完全な名前。
        """
        if not isinstance(node, _DEF):
            return
        qualname = f"{parent}.{node.name}"
        kind = "class" if isinstance(node, ast.ClassDef) else "function"
        self.definitions.append(
            Definition(qualname, self.name, kind, rel_path, node.lineno, _signature(node))
        )
        if isinstance(node, ast.ClassDef):
            self.refs.update(
                (qualname, t) for b in node.bases if (t := _target(b, self.names, None))
            )
            for child in _statements(node.body):
                self.visit(child, qualname, rel_path, qualname)
            return
        inner = [n for n in ast.walk(node) if isinstance(n, ast.Import | ast.ImportFrom)]
        local, _ = _imports(
            self.name, inner, self.is_package
        )  # 関数の中の import はこの関数だけで効く
        args = _arg_names(node)
        names = {k: v for k, v in {**self.names, **local}.items() if k not in args}
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call) and (t := _target(sub.func, names, cls)):
                self.refs.add((qualname, t))


def _read(src: Path, path: Path) -> _Module | None:
    """1 つのファイルを読み、定義と参照を集める。構文エラーなどで読めなければ None。"""
    try:
        tree = ast.parse(path.read_bytes(), str(path))  # BOM と coding 宣言は ast が解釈する
    except (SyntaxError, ValueError, OSError):
        return None
    name = module_name(src, path)
    is_package = path.name == "__init__.py"
    names, _ = _imports(name, list(_statements(tree.body)), is_package)
    every = [n for n in ast.walk(tree) if isinstance(n, ast.Import | ast.ImportFrom)]
    _, targets = _imports(name, every, is_package)  # 依存は関数の中の import も含めて数える
    for node in _statements(tree.body):
        if isinstance(node, _DEF):
            names[node.name] = f"{name}.{node.name}"
    mod = _Module(name, names, is_package, targets)
    for node in _statements(tree.body):
        mod.visit(node, name, path.relative_to(src).as_posix())
    return mod


def _owning_module(name: str, modules: dict[str, _Module]) -> str:
    """完全な名前を、それを含むプロジェクト内のいちばん長いモジュール名に縮める。外部なら空文字。"""
    parts = name.split(".")
    for end in range(len(parts), 0, -1):
        candidate = ".".join(parts[:end])
        if candidate in modules:
            return candidate
    return ""


def _resolve(name: str, modules: dict[str, _Module], defs: dict[str, Definition]) -> str:
    """`__init__.py` などで再公開した名前を、定義の場所までたどる（たどれなければそのまま返す）。"""
    for _ in range(10):  # 再公開の連鎖が循環していても止まるように回数を区切る
        mod = _owning_module(name, modules)
        if name in defs or not mod or name == mod:
            return name
        first, *rest = name[len(mod) + 1 :].split(".")
        alias = modules[mod].names.get(first)
        if not alias or alias == f"{mod}.{first}":
            return name
        name = ".".join([alias, *rest])
    return name


def build(src: Path) -> Graph:
    """`src` の下の全モジュールを読み、関係グラフを作る。

    Args:
        src: パッケージを置いたディレクトリ。無ければ空のグラフを返す（初めての PR の base など）。

    Returns:
        定義・プロジェクト内の import・モジュールをまたぐ呼び出しと継承をまとめたグラフ。
    """
    graph = Graph()
    if not src.is_dir():
        return graph
    modules: dict[str, _Module] = {}
    for path in sorted(p for p in src.rglob("*.py") if p.is_file()):
        mod = _read(src, path)
        if mod is None:
            graph.unreadable.append(path.relative_to(src).as_posix())
            continue
        modules[mod.name] = mod
        graph.definitions.update((d.qualname, d) for d in mod.definitions)
    defs = graph.definitions
    for mod in modules.values():
        for target in mod.targets:
            dep = _owning_module(target, modules)
            if dep and dep != mod.name:
                graph.imports.add((mod.name, dep))
        for a, b in mod.refs:
            b = _resolve(b, modules, defs)
            if b in defs and defs[a].module != defs[b].module:
                graph.calls.add((a, b))
    return graph


def _code(text: str) -> str:
    """Markdown のインラインコードにする。長すぎれば切り、中のバッククォートより長い囲みを使う。"""
    if len(text) > MAX_SIGNATURE:
        text = text[:MAX_SIGNATURE] + "…"
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    if not longest:
        return f"`{text}`"
    fence = "`" * (longest + 1)
    return f"{fence} {text} {fence}"


def _bullets(items: list[str]) -> list[str]:
    """箇条書きの行を作り、多すぎる分は件数だけにまとめる。"""
    lines = [f"- {item}" for item in items[:MAX_ITEMS]]
    if len(items) > MAX_ITEMS:
        lines.append(f"- ほか {len(items) - MAX_ITEMS} 件")
    return lines


def _section(title: str, items: list[str]) -> list[str]:
    """見出しと箇条書きの節を作る。項目が無ければ節ごと出さない。"""
    return [f"### {title}（{len(items)} 件）", "", *_bullets(items), ""] if items else []


def _import_section(added: set[tuple[str, str]], removed: set[tuple[str, str]]) -> list[str]:
    """モジュールどうしの import の増減を Mermaid の図にする。ノードの ID は通し番号にする。"""
    if not added and not removed:
        return []
    edges = [(a, b, "-->|増|") for a, b in sorted(added)] + [
        (a, b, "-.->|減|") for a, b in sorted(removed)
    ]
    ids: dict[str, str] = {}

    def node(name: str) -> str:
        ids.setdefault(name, f"n{len(ids)}")
        return f'{ids[name]}["{name}"]'

    lines = [
        f"### モジュールの依存（import）の増減（増 {len(added)}・減 {len(removed)}）",
        "",
        "```mermaid",
        "graph LR",
    ]
    lines += [f"  {node(a)} {arrow} {node(b)}" for a, b, arrow in edges[:MAX_ITEMS]]
    lines += ["```", ""]
    if len(edges) > MAX_ITEMS:
        lines += [f"図に入らなかった増減がほか {len(edges) - MAX_ITEMS} 件あります。", ""]
    return lines


def diff_markdown(base: Graph, head: Graph) -> str:
    """2 つの版のグラフを比べ、PR に貼る Markdown を作る。

    Args:
        base: 変更前（PR の向き先のブランチ）のグラフ。
        head: 変更後（PR のブランチ）のグラフ。

    Returns:
        先頭に `MARKER` を置いた Markdown。CI はこの印で前回のコメントを探して上書きする。
    """
    kinds = {"class": "クラス", "function": "関数"}

    def place(d: Definition) -> str:
        return f"{_code(d.qualname)}（{kinds[d.kind]}、`{d.path}:{d.line}`）"

    old, new = base.definitions, head.definitions
    changed = [
        f"{place(new[q])}: {_code(old[q].signature)} → {_code(new[q].signature)}"
        for q in sorted(old.keys() & new.keys())
        if old[q].signature != new[q].signature
    ]
    calls = [f"増: {_code(a)} → {_code(b)}" for a, b in sorted(head.calls - base.calls)]
    calls += [f"減: {_code(a)} → {_code(b)}" for a, b in sorted(base.calls - head.calls)]
    body = [
        *_section("増えた定義", [place(new[q]) for q in sorted(new.keys() - old.keys())]),
        *_section("消えた定義", [place(old[q]) for q in sorted(old.keys() - new.keys())]),
        *_section("引数・戻り値・継承元が変わった定義", changed),
        *_import_section(head.imports - base.imports, base.imports - head.imports),
        *_section("モジュールをまたぐ呼び出し・継承の増減", calls),
        *_section(
            "読めなかったファイル（構文エラーなど。差分に入っていない）",
            [f"`{p}`" for p in head.unreadable],
        ),
        *_section(
            "base で読めなかったファイル（中の定義は「増えた」に出ることがある）",
            [f"`{p}`" for p in base.unreadable],
        ),
    ]
    lines = [
        MARKER,
        "## コードの関係の差分",
        "",
        "CI がこの PR の base と head のコードから自動で作りました。呼び出しは名前で解決した近似です。",
        "",
        *(body or ["関係の変化はありません。", ""]),
    ]
    text = "\n".join(lines)
    if len(text) > MAX_COMMENT:
        text = text[:MAX_COMMENT] + "\n\n（長すぎるため、ここで切りました。）\n"
    return text


def main(argv: list[str] | None = None) -> int:
    """コマンドラインから差分を作り、標準出力に Markdown を書く。

    Args:
        argv: コマンドライン引数。`None` なら `sys.argv` を使う。

    Returns:
        終了コード（常に 0。読めないファイルはコメントに書いて続ける）。
    """
    parser = argparse.ArgumentParser(
        description="2 つの版の src から、コードの関係の差分を Markdown で出す。"
    )
    parser.add_argument("--base", type=Path, required=True, help="変更前の src ディレクトリ")
    parser.add_argument("--head", type=Path, required=True, help="変更後の src ディレクトリ")
    args = parser.parse_args(argv)
    sys.stdout.write(diff_markdown(build(args.base), build(args.head)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
