""" Combine multiple runs of robot into a single report and log
"""

import sys
from pathlib import Path

from robot.rebot import rebot_cli

ROOT = Path(__file__).parent.parent.resolve()
ATEST = ROOT / "atest"
OUT = ATEST / "output"

OK = 0


def combine():
    """ combine the outputs
    """

    args = [
        "--outputdir",
        OUT,
        "--output",
        "output.xml",
        "--noncritical",
        "ospy:windows38",
        *sys.argv[1:],
        *OUT.glob("*.robot.xml"),
    ]
    rebot_cli(args, exit=False)
    return OK


if __name__ == "__main__":
    sys.exit(combine())
