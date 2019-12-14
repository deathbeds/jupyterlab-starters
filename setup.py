import re
from pathlib import Path

__version__ = re.findall(
    r"""__version__ = "(.*?)"$""",
    Path(__file__).parent / "src" / "jupyter_starters" / "_version"
)[0]

__import__("setuptools").setup(version=__version__)
