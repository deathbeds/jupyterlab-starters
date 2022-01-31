"""Tests of CLI features"""


from .._version import __version__
from ..json_ import loads
from ..schema.v2 import STARTERS

try:
    from ruamel_yaml import safe_load

    HAS_YAML = True
except ImportError:  # pragma: no cover
    HAS_YAML = False


def test_cli_version(script_runner):
    """does it report the version?"""
    ret = script_runner.run("jupyter", "starters", "--version")
    assert ret.success
    assert __version__ in ret.stdout


def test_cli_json(script_runner):
    """does it emit valid json?"""
    ret = script_runner.run("jupyter", "starters", "list", "--json")
    assert ret.success
    assert STARTERS(loads(ret.stdout))


if HAS_YAML:

    def test_cli_yaml(script_runner):
        """is the default output valid yaml?"""

        ret = script_runner.run("jupyter", "starters", "list")
        assert ret.success
        assert safe_load(ret.stdout)
