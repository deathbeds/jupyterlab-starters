""" code quality countermeasures
"""
import sys
from pathlib import Path
from subprocess import call

OK = 0
FAIL = 1

ROOT = Path(__file__).parent.parent

PY_SRC = list((ROOT / "src").rglob("*.py"))
SCRIPTS = list((ROOT / "scripts").rglob("*.py"))

ALL_PY = [*PY_SRC, *SCRIPTS]


def lint():
    """ get that linty fresh feeling
    """
    return max(
        map(
            call,
            [
                ["isort", "-rc", *ALL_PY],
                ["black", *ALL_PY],
                ["flake8", *ALL_PY],
                ["pylint", *ALL_PY],
                ["mypy", *PY_SRC],
            ],
        )
    )


if __name__ == "__main__":
    sys.exit(lint())
