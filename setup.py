import re
from pathlib import Path


__import__("setuptools").setup(
    version=re.findall(
        r"""__version__ = "(.*?)"$""",
        (Path(__file__).parent / "src" / "jupyter_starters" / "_version.py").read_text()
    )[0],
    data_files=[
        (
            "etc/jupyter/jupyter_notebook_config.d",
            ["py_src/jupyter_lsp/etc/jupyter-starters-serverextension.json"],
        )
    ],

)
