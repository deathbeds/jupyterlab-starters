""" prepare built assets for release
"""
from subprocess import check_call


def release():
    """ build them
    """
    setup = ["python", "setup.py"]
    check_call([*setup, "sdist"])
    check_call([*setup, "bdist_wheel"])
    check_call(["jlpm", "bundle"])


if __name__ == "__main__":
    release()
