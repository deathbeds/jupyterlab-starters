import os

from ._version import __version__  # noqa

from .serverextension import load_jupyter_server_extension


def _jupyter_server_extension_paths():
    return [{"module": "jupyter_starters"}]
