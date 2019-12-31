""" test the sanity of the src/py_src behavior
"""
import pytest


@pytest.mark.parametrize(
    "name,starter",
    [
        ["doesn't exist", {"src": "doesnt-exist"}],
        ["not inside", {"py_src": "jupyter_starters", "src": "../"}],
    ],
)
def test_bad_src(starter_manager, name, starter):
    """ these are bad sources
    """
    assert starter_manager.resolve_src(starter) is None, f"{name} should have been None"
