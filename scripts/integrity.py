"""Check internal version consistency.

these should be quick to run (not invoke any other process)
"""
# pylint: disable=redefined-outer-name,unused-variable
import json
import pathlib
import re
import sys
import tempfile
from importlib.util import find_spec

import jsonschema
import pytest

ROOT = pathlib.Path.cwd()

# docs
MAIN_README = ROOT / "README.md"
CHANGELOG = ROOT / "CHANGELOG.md"

# TS stuff
NPM_NS = "@deathbeds"
PACKAGES = {
    package["name"]: [path.parent, package]
    for path, package in [
        (path, json.loads(path.read_text()))
        for path in ROOT.glob("packages/*/package.json")
    ]
}
MAIN_NAME = f"{NPM_NS}/jupyterlab-starters"
META_NAME = f"{NPM_NS}/metapackage-jupyterlab-starters"
RJSF_NAME = f"{NPM_NS}/jupyterlab-rjsf"

MAIN_EXT_VERSION = PACKAGES[MAIN_NAME][1]["version"]
RJSF_EXT_VERSION = PACKAGES[RJSF_NAME][1]["version"]

# py stuff
PY_NAME = "jupyter_starters"
_VERSION_PY = ROOT / "src" / "jupyter_starters" / "_version.py"
PY_VERSION = re.findall(r'= "(.*)"$', (_VERSION_PY).read_text())[0]


@pytest.fixture(scope="module")
def the_meta_package():
    """Load up the metapackage."""
    meta_path, meta = PACKAGES[META_NAME]
    return (
        meta_path,
        meta,
        json.loads((meta_path / "src/tsconfig.json").read_text()),
        (meta_path / "src" / "index.ts").read_text(),
    )


@pytest.mark.parametrize(
    "name,info", [p for p in PACKAGES.items() if p[0] != META_NAME]
)
def test_ts_package_integrity(name, info, the_meta_package):
    """Are the typescript packages self-consistent."""
    m_path, m_pkg, m_tsconfig, m_index = the_meta_package
    path, pkg = info

    assert (
        name in m_pkg["dependencies"]
    ), f"{name} missing from metapackage/package.json"

    assert f"'{name}'" in m_index, f"{name} missing from metapackage/src/index.ts"

    assert [
        ref
        for ref in m_tsconfig["references"]
        if ref["path"] == f"../../{path.name}/src"
    ], f"{name} missing from metapackage/tsconfig.json"

    schemas = list(path.glob("schema/*.json"))

    if schemas:
        for schema in schemas:
            schema_instance = json.loads(schema.read_text())
            jsonschema.validators.Draft7Validator(schema_instance)


@pytest.mark.parametrize(
    "pkg,version",
    [
        [PY_NAME, PY_VERSION],
        [MAIN_NAME, MAIN_EXT_VERSION],
        [RJSF_NAME, RJSF_EXT_VERSION],
    ],
)
def test_changelog_versions(pkg, version):
    """is the changelog up-to-date(ish)"""
    assert f"## `{pkg} {version}`" in CHANGELOG.read_text()


def integrity():
    """Run the integrity checks."""
    with tempfile.TemporaryDirectory() as tmpd:
        ini = pathlib.Path(tmpd) / "pytest.ini"
        ini.write_text(pathlib.Path(ROOT / "scripts" / "fake_pytest.ini").read_text())

        args = ["-c", str(ini), "-vv", __file__]
        try:
            if find_spec("pytest_azurepipelines"):
                args += ["--no-coverage-upload"]
        except ImportError:
            pass

        return pytest.main(args)


if __name__ == "__main__":
    sys.exit(integrity())
