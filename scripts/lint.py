""" code quality countermeasures
"""
import sys
from pathlib import Path
from subprocess import call

OK = 0
FAIL = 1

ROOT = Path(__file__).parent.parent

PY_SRC = list((ROOT / "src").rglob("*.py"))
PY_SCRIPTS = list((ROOT / "scripts").rglob("*.py"))
PY_ATEST = list((ROOT / "atest").rglob("*.py"))

ALL_PY = [*PY_SRC, *PY_SCRIPTS, *PY_ATEST]

ALL_ROBOT = list((ROOT / "atest").rglob("*.robot"))

RFLINT = ["--configure", "LineTooLong:200", "--configure", "TooFewKeywordSteps:0"]


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
                ["python", "-m", "robot.tidy", "--inplace", *ALL_ROBOT],
                ["rflint", *RFLINT, *ALL_ROBOT],
            ],
        )
    )


if __name__ == "__main__":
    sys.exit(lint())
