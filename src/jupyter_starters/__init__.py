""" starters for jupyterlab
"""
from ._version import __version__
from .serverextension import load_jupyter_server_extension


def _jupyter_server_extension_paths():
    return [{"module": "jupyter_starters"}]


def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": "@deathbeds/jupyterlab-starters"}]


__all__ = [
    "__version__",
    "_jupyter_labextension_paths",
    "_jupyter_server_extension_paths",
    "load_jupyter_server_extension",
]
