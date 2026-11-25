"""tools/changed_functions.py が、中身の変わった関数・メソッドだけを mutmut の名前で出すことを確かめる。"""

from pathlib import Path

import pytest
from tools import changed_functions


def _write(root: Path, files: dict[str, str]) -> Path:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


BASE = {
    "app/__init__.py": "def top() -> int:\n    return 1\n",
    "app/order.py": (
        "def keep() -> int:\n    return 1\n\n\n"
        "def body() -> int:\n    return 1\n\n\n"
        "def args() -> int:\n    return 1\n\n\n"
        "def gone() -> int:\n    return 1\n\n\n"
        "def outer() -> int:\n    def inner() -> int:\n        return 1\n\n    return inner()\n\n\n"
        "class Order:\n"
        "    def keep(self) -> int:\n        return 1\n\n"
        "    def body(self) -> int:\n        return 1\n\n"
        "    class Line:\n        def qty(self) -> int:\n            return 1\n"
    ),
}
HEAD = {
    "app/__init__.py": "def top() -> int:\n    return 2\n",
    "app/order.py": (
        "# コメントと空行を足しても、keep は変わっていない\n\n\n"
        "def keep() -> int:\n    return 1  # 行がずれただけ\n\n\n"
        "def body() -> int:\n    return 2\n\n\n"
        "def args(rate: int = 1) -> int:\n    return 1\n\n\n"
        "def outer() -> int:\n    def inner() -> int:\n        return 2\n\n    return inner()\n\n\n"
        "async def added() -> int:\n    return 1\n\n\n"
        "class Order:\n"
        "    def keep(self) -> int:\n        return 1\n\n"
        "    def body(self) -> int:\n        return 2\n\n"
        "    @staticmethod\n    def added() -> int:\n        return 1\n\n"
        "    class Line:\n        def qty(self) -> int:\n            return 2\n"
    ),
    "app/new.py": "def first() -> int:\n    return 1\n",
    "app/broken.py": "def (:\n",
}


def test_changed_lists_only_functions_whose_tree_differs(tmp_path: Path) -> None:
    base = _write(tmp_path / "base", BASE)
    head = _write(tmp_path / "head", HEAD)

    assert changed_functions.changed(base, head) == [
        "app.x_top",  # __init__.py はパッケージの名前になる
        "app.new.x_first",  # base に無いファイル
        "app.order.x_body",
        "app.order.x_args",  # 引数だけの変更
        "app.order.x_outer",  # 中の関数の変更は、外側の関数の変更になる
        "app.order.x_added",
        "app.order.xǁOrderǁbody",
        "app.order.xǁOrderǁadded",
    ]
    assert changed_functions.changed(head, head) == []
    assert changed_functions.changed(tmp_path / "missing", _write(tmp_path / "one", BASE)) == [
        "app.x_top",
        "app.order.x_keep",
        "app.order.x_body",
        "app.order.x_args",
        "app.order.x_gone",
        "app.order.x_outer",
        "app.order.xǁOrderǁkeep",
        "app.order.xǁOrderǁbody",
    ]


def test_main_prints_one_name_per_line(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    base = _write(tmp_path / "base", {"app/a.py": "def f() -> int:\n    return 1\n"})
    head = _write(
        tmp_path / "head",
        {"app/a.py": "def f() -> int:\n    return 2\n\n\ndef g() -> int:\n    return 1\n"},
    )

    assert changed_functions.main(["--base", str(base), "--head", str(head)]) == 0
    assert capsys.readouterr().out == "app.a.x_f\napp.a.x_g\n"
