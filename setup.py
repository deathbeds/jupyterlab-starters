import re
from pathlib import Path

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
        p.relative_to(HERE).as_posix() for p in ext_path.glob("*") if not p.is_dir()
    ]

ALL_FILES = sum(EXT_FILES.values(), [])

EXT_FILES[SHARE] += [str((ETC / "install.json").relative_to(HERE).as_posix())]

# TODO: replace with version file or package.json
VERSION_RE = r"""__version__ = "(.*?)"$"""

EXT_FILES.update(
    {
        "etc/jupyter/jupyter_server_config.d": [str(CONF.relative_to(HERE).as_posix())],
        "etc/jupyter/jupyter_notebook_config.d": [
            str(CONF.relative_to(HERE).as_posix())
        ],
    }
)

DATA_FILES = [(str(Path(tgt).as_posix()), src) for tgt, src in EXT_FILES.items()]

SETUP_ARGS = dict(
    version=re.findall(VERSION_RE, (SRC / "_version.py").read_text())[0],
    data_files=DATA_FILES,
)

if __name__ == "__main__":
    import pprint
    import sys

    import setuptools

    if "sdist" in sys.argv or "bdist_wheel" in sys.argv:
        remote_entry = [
            p for p in ALL_FILES if "remoteEntry" in str(p) and str(p).endswith(".js")
        ]
        if len(remote_entry) != 1:
            print(
                f"""
                Expected _exactly one_ remoteEntry.*.js, found.
                    {pprint.pformat(remote_entry)}
                Please run:

                   git clean -dxf src
                   doit dist
            """
            )
            sys.exit(1)

    setuptools.setup(**SETUP_ARGS)
