"""Single source of truth for jupyter_starts version."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
_D = HERE / "_d"
__ext__ = "@deathbeds/jupyterlab-starters"
__package_json__ = (
    _D if _D.exists() else Path(sys.prefix)
) / f"share/jupyter/labextensions/{ __ext__}/package.json"

__js__ = json.loads(__package_json__.read_text(encoding="utf-8"))
__version__ = __js__["version"].replace("-alpha", "a").replace("-beta", "b")
