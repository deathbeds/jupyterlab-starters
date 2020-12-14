""" check internal version consistency

    these should be quick to run (not invoke any other process)
"""
# pylint: disable=redefined-outer-name,unused-variable
import json
import pathlib
import re
import sys
import tempfile

import jsonschema
import pytest

try:
    import ruamel.yaml as yaml
except ImportError:
    import ruamel_yaml as yaml

ROOT = pathlib.Path.cwd()

# docs
MAIN_README = ROOT / "README.md"
CHANGELOG = ROOT / "CHANGELOG.md"

# dependencies
ENV = yaml.safe_load((ROOT / "environment.yml").read_text())
LAB_SPEC = [
    d.split(" ", 1)[1]
    for d in ENV["dependencies"]
    if isinstance(d, str) and d.startswith("jupyterlab ")
][0]

# TS stuff
NPM_NS = "@deathbeds"
PACKAGES = {
    package["name"]: [path.parent, package]
    for path, package in [
        (path, json.loads(path.read_text()))
        for path in ROOT.glob("packages/*/package.json")
    ]
}
MAIN_NAME = "{}/jupyterlab-starters".format(NPM_NS)
META_NAME = "{}/metapackage-jupyterlab-starters".format(NPM_NS)
RJSF_NAME = "{}/jupyterlab-rjsf".format(NPM_NS)

MAIN_EXT_VERSION = PACKAGES[MAIN_NAME][1]["version"]
RJSF_EXT_VERSION = PACKAGES[RJSF_NAME][1]["version"]

# py stuff
PY_NAME = "jupyter_starters"
_VERSION_PY = ROOT / "src" / "jupyter_starters" / "_version.py"
PY_VERSION = re.findall(r'= "(.*)"$', (_VERSION_PY).read_text())[0]

# CI stuff
PIPE_FILE = ROOT / "azure-pipelines.yml"
PIPELINES = yaml.safe_load(PIPE_FILE.read_text())
PIPE_VARS = PIPELINES["variables"]

CI = ROOT / "ci"


@pytest.fixture(scope="module")
def the_meta_package():
    """load up the metapackage"""
    meta_path, meta = PACKAGES[META_NAME]
    return (
        meta_path,
        meta,
        json.loads((meta_path / "tsconfig.json").read_text()),
        (meta_path / "src" / "index.ts").read_text(),
    )


@pytest.mark.parametrize("name,env_path", [["docs", ROOT / "docs" / "environment.yml"]])
def test_env_versions(name, env_path):
    """are special environments in sync with the main demo/development env?"""
    env = yaml.safe_load(env_path.read_text())
    for package in ENV["dependencies"]:
        assert package in env["dependencies"], f"{package} in {name} is out-of-date"


@pytest.mark.parametrize(
    "name,version",
    [
        ["PY_JLST_VERSION", PY_VERSION],
        ["JS_JLST_VERSION", MAIN_EXT_VERSION],
        ["JS_RJSF_VERSION", RJSF_EXT_VERSION],
    ],
)
def test_ci_variables(name, version):
    """are CI variables right?
    npm includes a -
    """
    if name.startswith("JS"):
        assert PIPE_VARS[name].replace("-", "") == version
    else:
        assert PIPE_VARS[name] == version


@pytest.mark.parametrize(
    "name,info", [p for p in PACKAGES.items() if p[0] != META_NAME]
)
def test_ts_package_integrity(name, info, the_meta_package):
    """are the typescript packages self-consistent"""
    m_path, m_pkg, m_tsconfig, m_index = the_meta_package
    path, pkg = info

    assert (
        name in m_pkg["dependencies"]
    ), "{} missing from metapackage/package.json".format(name)

    assert (
        "'{}'".format(name) in m_index
    ), "{} missing from metapackage/src/index.ts".format(name)

    assert [
        ref
        for ref in m_tsconfig["references"]
        if ref["path"] == "../{}".format(path.name)
    ], "{} missing from metapackage/tsconfig.json".format(name)

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
    assert "## `{} {}`".format(pkg, version) in CHANGELOG.read_text()


PYTEST_INI = """
[pytest]
junit_family = xunit2
"""


def integrity():
    """run the tests"""
    with tempfile.TemporaryDirectory() as tmpd:
        ini = pathlib.Path(tmpd) / "pytest.ini"
        ini.write_text(PYTEST_INI)

        return pytest.main(["-c", str(ini), "-vv", __file__])


if __name__ == "__main__":
    sys.exit(integrity())
