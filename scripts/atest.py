""" Run acceptance tests with robot framework
"""
import os
import platform
import shutil
import sys
from pathlib import Path

import robot

ROOT = Path(__file__).parent.parent.resolve()
ATEST = ROOT / "atest"
OUT = ATEST / "output"

OS = platform.system()
PY = "".join(map(str, sys.version_info[:2]))

OK = 0


def atest(attempt=0):
    """ run the acceptance tests once
    """
    # pylint: disable=broad-except
    stem = "_".join([OS, PY, str(attempt)]).replace(".", "_").lower()
    out_dir = OUT / stem

    args = [
        "--name",
        f"{OS}{PY}",
        "--outputdir",
        out_dir,
        "--output",
        OUT / f"{stem}.robot.xml",
        "--log",
        OUT / f"{stem}.log.html",
        "--report",
        OUT / f"{stem}.report.html",
        "--xunit",
        OUT / f"{stem}.xunit.xml",
        "--variable",
        f"OS:{OS}",
        "--variable",
        f"PY:{PY}",
        "--noncritical",
        "ospy:windows38",
        "--xunitskipnoncritical",
        *sys.argv[1:],
        ATEST,
    ]

    os.chdir(ATEST)

    if out_dir.exists():
        print("trying to clean out {}".format(out_dir))
        try:
            shutil.rmtree(out_dir)
        except Exception as err:
            print("Error deleting {}, hopefully harmless: {}".format(out_dir, err))

    return robot.run_cli(list(map(str, args)), exit=False)


def attempt_atest(retries=int(os.environ.get("ATEST_RETRIES") or "0")):
    """ try acceptance tests a few times
    """
    attempt = 0
    code = -1

    while code != OK and attempt <= retries:
        attempt += 1
        print("attempt {} of {}...".format(attempt, retries + 1))
        code = atest(attempt)

    return code


if __name__ == "__main__":
    sys.exit(attempt_atest())
