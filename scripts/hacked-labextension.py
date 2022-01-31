"""https://github.com/jupyterlab/jupyterlab/issues/9959"""
import sys
from pathlib import Path

from jupyterlab import federated_labextensions
from jupyterlab.labextensions import LabExtensionApp

HERE = Path(__file__).parent
ROOT = HERE.parent
NODE_MODULES = ROOT / "node_modules"
BUILDER = NODE_MODULES / "@jupyterlab" / "builder" / "lib" / "build-labextension.js"


def _ensure_builder(*args, **kwargs):
    return str(BUILDER)


def _get_labextension_metadata(module):
    try:
        import jupyter_starters
    except Exception as err:
        print("Failed to import jupyter_starters", err)
        raise err
    return jupyter_starters, jupyter_starters._jupyter_labextension_paths()


federated_labextensions._ensure_builder = _ensure_builder
federated_labextensions._get_labextension_metadata = _get_labextension_metadata

main = LabExtensionApp.launch_instance

if __name__ == "__main__":
    sys.exit(main())
