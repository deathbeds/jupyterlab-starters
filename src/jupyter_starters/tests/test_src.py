""" test the sanity of the src/py_src behavior
"""
# pylint: disable=too-many-arguments
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "name,starter",
    [
        ["doesn't exist", {"src": "doesnt-exist"}],
        ["not importable", {"py_src": "not_a_module", "src": "doesnt-matter"}],
        ["no src", {"py_src": "won't matter"}],
        ["nothing", {}],
    ],
)
def test_bad_src(starter_manager, name, starter):
    """these are bad sources"""
    src = starter_manager.resolve_src(starter)
    assert src is None, f"{name} should have been None"


@pytest.mark.parametrize(
    "name,starter,py_path",
    [
        ["local file", {"src": "README.md"}, False],
        ["local directory", {"src": "my_module/starter_content"}, False],
        ["py file", {"src": "__init__.py", "py_src": "my_module"}, True],
        ["py directory", {"src": "starter_content", "py_src": "my_module"}, True],
    ],
)
def test_good_src(
    name, starter, py_path, monkeypatch, example_project, starter_manager
):
    """these are good sources"""
    if py_path:
        monkeypatch.syspath_prepend(example_project)
    else:
        monkeypatch.chdir(example_project)

    src = starter_manager.resolve_src(starter)
    assert src and isinstance(src, Path) and src.exists(), f"{name} {src} is bad"
