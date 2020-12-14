""" Run acceptance tests with robot framework
"""
import os
import platform
import shutil
import sys
import time
from pathlib import Path

import robot

ROOT = Path(__file__).parent.parent.resolve()
ATEST = ROOT / "atest"
OUT = ATEST / "output"

OS = platform.system()
PY = "".join(map(str, sys.version_info[:2]))


OS_PY_ARGS = {
    # e.g. when notebook and ipykernel releases did not yet support python 3.8
    #      on windows
    #
    # ("Windows", "38"): ["--include", "not-supported", "--runemptysuite"]
}

OK = 0


def get_stem(attempt, extra_args):
    """predictable folder naming, based on attempt an other extra args"""
    stem = "_".join([OS, PY, str(attempt)]).replace(".", "_").lower()

    if "--dryrun" in extra_args:
        stem = f"dry_run_{stem}"

    return stem


def atest(attempt, extra_args):
    """perform a single attempt of the acceptance tests"""
    extra_args += OS_PY_ARGS.get((OS, PY), [])
    stem = get_stem(attempt, extra_args)

    if attempt != 1:
        previous = OUT / f"{get_stem(attempt - 1, extra_args)}.robot.xml"
        if previous.exists():
            extra_args += ["--rerunfailed", str(previous)]

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
        "--xunitskipnoncritical",
        "--randomize",
        "all",
        *(extra_args or []),
        ATEST,
    ]

    print("Robot Arguments\n", " ".join(["robot"] + list(map(str, args))))

    os.chdir(ATEST)

    if out_dir.exists():
        print("trying to clean out {}".format(out_dir))
        shutil.rmtree(out_dir, ignore_errors=True)

    try:
        robot.run_cli(list(map(str, args)))
        return 0
    except SystemExit as err:
        return err.code


def attempt_atest_with_retries(*extra_args):
    """retry the robot tests a number of times"""
    attempt = 0
    error_count = -1

    retries = int(os.environ.get("ATEST_RETRIES") or "0")

    while error_count != 0 and attempt <= retries:
        attempt += 1
        print("attempt {} of {}...".format(attempt, retries + 1))
        start_time = time.time()
        error_count = atest(attempt=attempt, extra_args=list(extra_args))
        print(error_count, "errors in", int(time.time() - start_time), "seconds")

    return error_count


if __name__ == "__main__":
    sys.exit(attempt_atest_with_retries(*sys.argv[1:]))
