import re
from pathlib import Path


import re
from pathlib import Path

import setuptools

HERE = Path(__file__).parent
SRC = HERE / "src" / "jupyter_starters"
ETC = SRC / "etc"
CONF = ETC / "jupyter-starters-serverextension.json"
EXT = SRC / "labextension"
EXT_NAME = "@deathbeds/jupyterlab-starters"

EXT_FILES = {}
SHARE = f"share/jupyter/labextensions/{EXT_NAME}"

for ext_path in [EXT] + [d for d in EXT.rglob("*") if d.is_dir()]:
    if ext_path == EXT:
        target = SHARE
    else:
        target = f"{SHARE}/{ext_path.relative_to(EXT)}"
    EXT_FILES[target] = [
        p.relative_to(HERE).as_posix()
        for p in ext_path.glob("*")
        if not p.is_dir()
    ]

ALL_FILES = sum(EXT_FILES.values(), [])

assert (
    len([p for p in ALL_FILES if "remoteEntry" in str(p)]) == 1
), "expected _exactly one_ remoteEntry.*.js"

EXT_FILES[SHARE] += [ETC / "install.json"]

# TODO: replace with version file or package.json
VERSION_RE = r"""__version__ = "(.*?)"$"""

SETUP_ARGS = dict(
    version=re.findall(VERSION_RE, (SRC / "_version.py").read_text())[0],
    data_files=[
        ("etc/jupyter/jupyter_server_config.d", [str(CONF)]),
        ("etc/jupyter/jupyter_notebook_config.d", [str(CONF)]),
        *[(str(k), list(map(str, v))) for k, v in EXT_FILES.items()],
    ],
)

if __name__ == "__main__":
    setuptools.setup(**SETUP_ARGS)
