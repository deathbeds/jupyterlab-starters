""" release on pypi
"""
import os
from subprocess import check_call


def release(registry=None):
    """ do a (test) release
    """
    registry = registry or os.environ.get("PYPI_REGISTRY", "pypitest")
    setup = ["python", "setup.py"]
    check_call([*setup, "register", "-r", registry])
    check_call([*setup, "sdist"])
    check_call([*setup, "bdist_wheel"])
    check_call([*setup, "sdist", "upload", "-r", registry])
    check_call([*setup, "bdist_wheel", "upload", "-r", registry])


if __name__ == "__main__":
    release()
