import re
from pathlib import Path


import re
from pathlib import Path

import setuptools

HERE = Path(__file__).parent
EXT = HERE / "src" / "jupyter_starters" / "labextension"
EXT_NAME = "@deathbeds/jupyterlab-starters"

EXT_FILES = {}
SHARE = f"share/jupyter/labextensions/{EXT_NAME}"

for ext_path in [EXT] + [d for d in EXT.rglob("*") if d.is_dir()]:
    if ext_path == EXT:
        target = str(SHARE)
    else:
        target = f"{SHARE}/{ext_path.relative_to(EXT)}"
    EXT_FILES[target] = [
        str(p.relative_to(HERE).as_posix())
        for p in ext_path.glob("*")
        if not p.is_dir()
    ]

ALL_FILES = sum(EXT_FILES.values(), [])

assert (
    len([p for p in ALL_FILES if "remoteEntry" in str(p)]) == 1
), "expected _exactly one_ remoteEntry.*.js"

EXT_FILES[str(SHARE)] += ["src/jupyter_starters/etc/install.json"]


SETUP_ARGS = dict(
    version=re.findall(
        r"""__version__ = "(.*?)"$""",
        (Path(__file__).parent / "src" / "jupyter_starters" / "_version.py").read_text()
    )[0],
    data_files=[

        (
            "etc/jupyter/jupyter_server_config.d",
            ["src/jupyter_starters/etc/jupyter-starters-serverextension.json"],
        ),
        (
            "etc/jupyter/jupyter_notebook_config.d",
            ["src/jupyter_starters/etc/jupyter-starters-serverextension.json"],
        ),
        *[(k, v) for k, v in EXT_FILES.items()],
    ],

)

if __name__ == "__main__":
    setuptools.setup(**SETUP_ARGS)
