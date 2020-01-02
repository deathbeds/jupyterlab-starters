""" code quality countermeasures
"""
import sys
from pathlib import Path
from subprocess import call

from nbformat import NO_CONVERT, read, write

OK = 0
FAIL = 1

ROOT = Path(__file__).parent.parent

PY_SRC = list((ROOT / "src").rglob("*.py"))
PY_SCRIPTS = list((ROOT / "scripts").rglob("*.py"))
PY_DOCS = list((ROOT / "docs").rglob("*.py"))
PY_ATEST = list((ROOT / "atest").rglob("*.py"))

NB_DOCS = list((ROOT / "docs").rglob("*.ipynb"))
NB_EXAMPLES = list((ROOT / "examples").rglob("*.ipynb"))

ALL_NB = [*NB_DOCS, *NB_EXAMPLES]
ALL_PY = [*PY_SRC, *PY_SCRIPTS, *PY_ATEST, *PY_DOCS]

ALL_ROBOT = list((ROOT / "atest").rglob("*.robot"))

RFLINT_RULES = [
    "LineTooLong:200",
    "TooFewKeywordSteps:0",
    "TooManyTestSteps:30",
]

RFLINT = sum([["--configure", rule] for rule in RFLINT_RULES], [])


def nblint():
    """ clean up notebooks
    """
    for nbp in ALL_NB:
        nbf = read(str(nbp), NO_CONVERT)
        changed = False
        for cell in nbf.cells:
            if cell.cell_type == "code":
                if cell.outputs:
                    cell.outputs = []
                    changed = True
                if cell.execution_count:
                    cell.execution_count = None
                    changed = True

        if not nbf.cells[-1].source.strip():
            nbf.cells = nbf.cells[:-1]
            changed = True

        if changed:
            print(f"Overwriting {nbp}")
            write(nbf, str(nbp))

    return 0


def lint():
    """ get that linty fresh feeling
    """
    nblint()

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
