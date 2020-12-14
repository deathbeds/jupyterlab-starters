""" run python unit tests with pytest
"""
import platform
import sys

import pytest

OS = platform.system()
PY = "".join(map(str, sys.version_info[:2]))

SKIPS = {("Windows", "38"): ["-k", "not notebook"]}


def utest(*extra_args):
    """run the tests"""
    args = [
        "--pyargs",
        "jupyter_starters",
        "--cov",
        "jupyter_starters",
        "--cov-report",
        "term-missing:skip-covered",
        "-p",
        "no:warnings",
        "--flake8",
        # "--cov-fail-under=100",
        *SKIPS.get((OS, PY), []),
        "-vv",
    ] + list(extra_args)

    return pytest.main(args)


if __name__ == "__main__":
    sys.exit(utest(*sys.argv[1:]))
