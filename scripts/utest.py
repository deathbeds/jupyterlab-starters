""" run python unit tests with pytest
"""
import sys

import pytest


def utest(*extra_args):
    """ run the tests
    """
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
        "-vv",
    ] + list(extra_args)

    return pytest.main(args)


if __name__ == "__main__":
    sys.exit(utest(*sys.argv[1:]))
