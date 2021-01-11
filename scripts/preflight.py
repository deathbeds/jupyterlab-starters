""" check preflight consistency
"""
import pathlib

# pylint: disable=redefined-outer-name,unused-variable
import re
import subprocess
import sys
import tempfile

import pytest

# TS stuff
NPM_NS = "@deathbeds"
MAIN_NAME = "{}/jupyterlab-starters".format(NPM_NS)

# py stuff
PY_NAME = "jupyter_starters"


@pytest.mark.parametrize(
    "kind,expect",
    [
        ["serverextension", f"{PY_NAME}.*OK"],
        ["labextension", f"{MAIN_NAME}.*enabled.*OK"],
    ],
)
def test_extension_cli(kind, expect):
    """does (at least) the CLI think the extensions are installed?"""
    proc = subprocess.Popen(
        ["jupyter", kind, "list"], stderr=subprocess.PIPE, stdout=subprocess.PIPE
    )
    out, err = proc.communicate()
    all_out = f"""{out.decode("utf-8")}{err.decode("utf-8")}"""
    assert re.findall(expect, all_out), f"failed to find {expect} in:\n{all_out}"


def preflight():
    """run the tests"""
    with tempfile.TemporaryDirectory() as tmpd:
        ini = pathlib.Path(tmpd) / "pytest.ini"
        ini.write_text("""\n[pytest]\njunit_family = xunit2\n""")

        return pytest.main(["-c", str(ini), "-vv", __file__])


if __name__ == "__main__":
    sys.exit(preflight())
