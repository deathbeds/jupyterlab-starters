"""Parametrized starter files and folders for Jupyter."""
from typing import Dict, List

from ._version import __js__, __package_json__, __version__
from .serverextension import load_jupyter_server_extension


def _jupyter_server_extension_paths() -> List[Dict[str, str]]:
    return [{"module": "jupyter_starters"}]


def _jupyter_labextension_paths() -> List[Dict[str, str]]:
    """Fetch the paths to JupyterLab extensions."""
    return [dict(src=(str(__package_json__.parent)), dest=__js__["name"])]


__all__ = [
    "__version__",
    "_jupyter_labextension_paths",
    "_jupyter_server_extension_paths",
    "load_jupyter_server_extension",
]
