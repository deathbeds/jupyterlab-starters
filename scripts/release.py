""" prepare built assets for release
"""
from pathlib import Path
import shutil
from subprocess import check_call


HERE = Path(__file__).parent
ROOT = HERE.parent
DIST = ROOT / "dist"
PACKAGES = ROOT / "packages"

def release():
    """build them"""
    DIST.exists() and shutil.rmtree(DIST)
    DIST.mkdir()
    check_call(["jlpm", "clean"])
    check_call(["jlpm", "build"])
    check_call(["jlpm", "bundle"])
    [shutil.copy2(tgz, DIST / tgz.name) for tgz in PACKAGES.glob("*/*.tgz")]
    setup = ["python", "setup.py"]
    check_call([*setup, "sdist"])
    check_call([*setup, "bdist_wheel"])

if __name__ == "__main__":
    release()
