""" release on pypi and npm
"""
import os
from subprocess import check_call

FOR_REAL = bool(os.environ.get("FOR_REAL", "0"))


def upload():
    """ upload releases
    """
    pypi_registry = (
        "https://test.pypi.org/legacy/" if FOR_REAL else "https://test.pypi.org/legacy/"
    )
    check_call(["twine", "upload", "--repository-url", pypi_registry, "dist/*"])

    if FOR_REAL:
        check_call(["jlpm", "upload"])


if __name__ == "__main__":
    upload()
