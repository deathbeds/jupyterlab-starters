""" release on pypi
"""
import os
from subprocess import check_call


def release(registry=None):
    """ do a (test) release
    """
    registry = registry or os.environ.get(
        "PYPI_REGISTRY", "https://test.pypi.org/legacy/"
    )
    setup = ["python", "setup.py"]
    check_call([*setup, "sdist"])
    check_call([*setup, "bdist_wheel"])
    check_call(["twine", "upload", "--repository-url", registry, "dist/*"])


if __name__ == "__main__":
    release()
