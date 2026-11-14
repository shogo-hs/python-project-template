"""tools/code_graph.py が、関数を消す・足す・依存を変える変更を差分に出すことを確かめる。"""

from pathlib import Path

from tools import code_graph


def _write(root: Path, files: dict[str, str]) -> Path:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


BASE = {
    "app/__init__.py": "",
    "app/domain/__init__.py": "",
    "app/domain/order.py": "class Order:\n    def total(self) -> int:\n        return 0\n\n\ndef old() -> None:\n    pass\n",
    "app/application/__init__.py": "",
    "app/application/service.py": "from app.domain.order import Order\n\n\ndef run() -> int:\n    return Order().total()\n",
}
HEAD = {
    **BASE,
    "app/domain/order.py": "class Order:\n    def total(self) -> int:\n        return 0\n",
    "app/application/service.py": (
        "from ..domain.order import Order\nfrom app.domain import tax\n\n\n"
        "def run(rate: int = 1) -> int:\n    return tax.add(Order().total())\n"
    ),
    "app/domain/tax.py": "def add(x: int) -> int:\n    return x\n",
}


def test_diff_shows_added_removed_and_new_dependencies(tmp_path: Path) -> None:
    base = code_graph.build(_write(tmp_path / "base", BASE))
    head = code_graph.build(_write(tmp_path / "head", HEAD))

    assert "app.domain.order.Order.total" in head.definitions
    assert ("app.application.service", "app.domain.order") in base.imports
    assert (
        "app.application.service",
        "app.domain.order",
    ) in head.imports  # 相対 import も同じ先になる
    assert ("app.application.service.run", "app.domain.tax.add") in head.calls

    md = code_graph.diff_markdown(base, head)
    assert md.startswith(code_graph.MARKER)
    assert "`app.domain.tax.add`（関数、`app/domain/tax.py:1`）" in md
    assert "`app.domain.order.old`" in md.split("### 消えた定義")[1]
    assert 'n0["app.application.service"] -->|増| n1["app.domain.tax"]' in md
    assert "増: `app.application.service.run` → `app.domain.tax.add`" in md
    assert (
        "`app.application.service.run`（関数、`app/application/service.py:5`）: `() -> int` → `(rate: int=1) -> int`"
        in md
    )


def test_no_change_and_missing_base(tmp_path: Path) -> None:
    head = code_graph.build(_write(tmp_path / "head", BASE))
    assert "関係の変化はありません" in code_graph.diff_markdown(head, head)
    first = code_graph.diff_markdown(code_graph.build(tmp_path / "missing"), head)
    assert "### 増えた定義（4 件）" in first


def test_hard_inputs(tmp_path: Path) -> None:
    files = {
        "p/__init__.py": "",
        "p/d/__init__.py": "from .order import Order\n",
        "p/d/order.py": "class Order:\n    pass\n",
        "p/b.py": "def g() -> None:\n    pass\n",
        "p/a_b.py": "import p.b\nfrom typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    from p.d import Order\n",
        "p/use.py": (
            "import p.b\nfrom p.d import Order\n\n\nclass Sub(Order):\n    pass\n\n\n"
            "try:\n    def h() -> None:\n        p.b.g()\nexcept ImportError:\n    pass\n"
        ),
        "p/broken.py": "def (:\n",
    }
    _write(tmp_path / "base", files)
    (tmp_path / "base" / "p" / "bom.py").write_bytes("\ufeffdef f() -> None:\n    pass\n".encode())
    base = code_graph.build(tmp_path / "base")
    head_files = {**files, "p/b.py": "async def g() -> None:\n    pass\n"}
    head = code_graph.build(_write(tmp_path / "head", head_files))

    assert "p.bom.f" in base.definitions  # BOM 付きでも読める
    assert base.unreadable == ["p/broken.py"]
    assert "p.use.h" in base.definitions  # try の中の定義
    assert ("p.use.Sub", "p.d.order.Order") in base.calls  # 再公開した名前を定義まで解決する
    assert ("p.use.h", "p.b.g") in base.calls  # p.b.g() の形
    assert (
        "p.a_b",
        "p.d",
    ) in base.imports  # TYPE_CHECKING の中の import（矢印は import した先に向く）

    md = code_graph.diff_markdown(base, head)
    assert "`p.b.g`（関数、`p/b.py:1`）: `() -> None` → `async () -> None`" in md
    assert "`p/broken.py`" in md


def test_function_local_import_and_args_do_not_leak(tmp_path: Path) -> None:
    files = {
        "p/__init__.py": "def lazy() -> None:\n    from p.impl import Real\n",
        "p/impl.py": "class Real:\n    pass\n",
        "p/b.py": "def g() -> None:\n    pass\n\n\ndef run() -> None:\n    pass\n",
        "p/c.py": "def g() -> None:\n    pass\n",
        "p/a.py": (
            "from p.b import g\n\n\ndef f() -> None:\n    g()\n\n\n"
            "def k() -> None:\n    from p.c import g\n    g()\n\n\n"
            "def m(run: object) -> None:\n    from p.b import run as _r\n    run()\n"
        ),
        "p/x.py": "from p import Real\n\n\ndef y() -> None:\n    Real()\n",
    }
    graph = code_graph.build(_write(tmp_path, files))
    assert ("p.a.f", "p.b.g") in graph.calls
    assert ("p.a.k", "p.c.g") in graph.calls
    assert ("p.a.f", "p.c.g") not in graph.calls
    assert not any(a == "p.a.m" for a, _ in graph.calls)  # 引数 run は import した名前ではない
    assert ("p.x.y", "p.impl.Real") not in graph.calls  # 関数の中の import は再公開ではない
    assert ("p.a", "p.b") in graph.imports
    assert ("p.a", "p.c") in graph.imports
    assert code_graph._code("x='``'") == "``` x='``' ```"
