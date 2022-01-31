""" check preflight consistency
"""
import pathlib

# pylint: disable=redefined-outer-name,unused-variable
import re
import subprocess
import sys
import tempfile
from importlib.util import find_spec

import pytest

ROOT = pathlib.Path(__file__).parent.parent

# TS stuff
NPM_NS = "@deathbeds"
MAIN_NAME = f"{NPM_NS}/jupyterlab-starters"

# py stuff
PY_NAME = "jupyter_starters"


@pytest.mark.parametrize(
    "kind,expect",
    [
        ["serverextension", f"{PY_NAME}.*ok"],
        ["labextension", f"{MAIN_NAME}.*enabled.*ok"],
    ],
)
def test_extension_cli(kind, expect):
    """does (at least) the CLI think the extensions are installed?"""
    proc = subprocess.Popen(
        ["jupyter", kind, "list"], stderr=subprocess.PIPE, stdout=subprocess.PIPE
    )
    out, err = proc.communicate()
    all_out = f"""{out.decode("utf-8")}{err.decode("utf-8")}""".lower()
    assert re.findall(expect, all_out), f"failed to find {expect} in:\n{all_out}"


def preflight():
    """run the tests"""
    with tempfile.TemporaryDirectory() as tmpd:
        ini = pathlib.Path(tmpd) / "pytest.ini"
        ini.write_text((ROOT / "scripts" / "fake_pytest.ini").read_text())

        args = ["-c", str(ini), "-vv", __file__]
        try:
            if find_spec("pytest_azurepipelines"):
                args += ["--no-coverage-upload"]
        except ImportError:
            pass

        return pytest.main(args)


if __name__ == "__main__":
    sys.exit(preflight())
