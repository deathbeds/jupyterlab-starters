"""development automation for jupyter[lab]-starter"""
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import typing
from datetime import datetime
from hashlib import sha256
from pathlib import Path

import doit.reporter
import doit.tools
from ruamel_yaml import safe_load


def task_lock():
    """generate conda locks for all envs"""
    if C.SKIP_LOCKS:
        return

    yield U.lock("build", C.DEFAULT_PY, C.DEFAULT_SUBDIR, ["node", "lab", "lint"])
    yield U.lock(
        "binder", C.DEFAULT_PY, C.DEFAULT_SUBDIR, ["run", "lab", "node", "docs"]
    )

    for subdir in C.SUBDIRS:
        for py in C.PYTHONS:
            yield U.lock("atest", py, subdir, ["run", "lab", "utest"])
        yield U.lock(
            "docs",
            C.DEFAULT_PY,
            subdir,
            ["node", "build", "lint", "atest", "utest", "lab", "run"],
        )


def task_env():
    if C.CI or C.DEMO_IN_BINDER:
        return
    yield dict(
        name="dev",
        file_dep=[P.DEV_LOCKFILE],
        actions=[
            ["mamba", "create", "--prefix", P.DEV_PREFIX, "--file", P.DEV_LOCKFILE]
        ],
        targets=[P.DEV_HISTORY],
    )


def task_lint():
    """improve and ensure code quality"""
    if C.DOCS_IN_CI or C.TEST_IN_CI or C.DEMO_IN_BINDER:
        return

    yield dict(
        name="py:isort:black",
        **U.run_in(
            "docs",
            [[*C.PYM, "isort", *P.ALL_PY], [*C.PYM, "black", "--quiet", *P.ALL_PY]],
            file_dep=[*P.ALL_PY],
        ),
    )

    for linter, file_dep_cmd in {
        "flake8": [P.ALL_PY, [*C.PYM, "flake8"]],
        "pylint": [P.PY_SRC, [*C.PYM, "pylint", "--reports", "n", "--score", "n"]],
        "mypy": [
            P.PY_SRC,
            [*C.PYM, "mypy", "--no-error-summary", "--config-file", P.SETUP_CFG],
        ],
    }.items():
        file_dep, cmd = file_dep_cmd
        yield dict(
            name=f"py:{linter}",
            task_dep=["lint:py:isort:black"],
            **U.run_in("docs", [cmd + file_dep], file_dep=[P.SETUP_CFG, *file_dep]),
        )

    yield dict(
        name="rf:tidy",
        **U.run_in(
            "docs",
            [[*C.PYM, "robot.tidy", "--inplace", *P.ALL_ROBOT]],
            file_dep=P.ALL_ROBOT,
        ),
    )

    rflint = [
        *C.PYM,
        "rflint",
        *sum([["--configure", rule] for rule in C.RFLINT_RULES], []),
    ]

    yield dict(
        name="rf:rflint",
        task_dep=["lint:rf:tidy"],
        **U.run_in("docs", [rflint + P.ALL_ROBOT], file_dep=P.ALL_ROBOT),
    )

    prettier = [C.JLPM, "prettier"] + (
        ["--write", "--list-different"] if C.RUNNING_LOCALLY else ["--check"]
    )

    yield dict(
        name="prettier",
        **U.run_in(
            "docs",
            [[*prettier, *P.ALL_PRETTIER]],
            file_dep=[
                P.YARN_INTEGRITY,
                *[p for p in P.ALL_PRETTIER if not p.name.startswith("_")],
            ],
        ),
    )

    eslint = [C.JLPM, "eslint", "--ext", ".js,.jsx,.ts,.tsx"] + (
        ["--fix"] if C.RUNNING_LOCALLY else []
    )

    yield dict(
        name="eslint",
        task_dep=["lint:prettier"],
        **U.run_in(
            "docs",
            [[*eslint, P.PACKAGES]],
            file_dep=[
                P.YARN_INTEGRITY,
                *[p for p in P.ALL_TS if not p.name.startswith("_")],
                *P.ROOT.glob(".eslint*"),
            ],
        ),
    )

    nblint = P.SCRIPTS / "nblint.py"

    for ipynb in P.ALL_IPYNB:
        yield dict(
            name=f"ipynb:{ipynb.relative_to(P.ROOT)}",
            **U.run_in(
                "docs",
                [[C.PY, nblint, ipynb]],
                file_dep=[P.YARN_INTEGRITY, nblint],
            ),
        )


def task_jlpm():
    if C.DOCS_IN_CI or C.TEST_IN_CI:
        return

    if C.SKIP_JLPM_IF_CACHED and P.YARN_INTEGRITY.exists():
        return

    jlpm_args = ["--frozen-lockfile"] if C.CI else []

    yield dict(
        name="install",
        **U.run_in(
            "build",
            [[C.JLPM, *jlpm_args]],
            file_dep=[P.YARNRC, *P.ALL_PACKAGE_JSON],
            targets=[P.YARN_INTEGRITY],
        ),
    )


def task_build():
    """build intermediate artifacts"""
    if C.DOCS_IN_CI or C.TEST_IN_CI:
        return

    yield dict(
        name="lerna:pre",
        **U.run_in(
            "build",
            [
                [C.JLPM, "lerna", "run", "--stream", "build:pre"],
                [
                    C.JLPM,
                    "prettier",
                    "--write",
                    P.JS_SRC_SCHEMA,
                    P.JS_LIB_SCHEMA,
                    P.JS_SRC_SCHEMA_D_TS,
                ],
            ],
            file_dep=[
                P.YARN_INTEGRITY,
                *P.ALL_PY_SCHEMA,
                *P.ALL_PACKAGE_JSON,
                P.YARN_LOCK,
            ],
            targets=[P.JS_SRC_SCHEMA, P.JS_LIB_SCHEMA, P.JS_SRC_SCHEMA_D_TS],
        ),
    )

    yield dict(
        name="lerna:lib",
        **U.run_in(
            "build",
            [
                [C.JLPM, "lerna", "run", "--stream", "build"],
            ],
            file_dep=[
                *P.ALL_PACKAGE_JSON,
                *P.ALL_TS,
                *P.ALL_TSCONFIG,
                P.JS_SRC_SCHEMA_D_TS,
                P.JS_SRC_SCHEMA,
                P.YARN_INTEGRITY,
                P.YARN_LOCK,
            ],
            targets=[P.TSBUILDINFO],
        ),
    )

    yield dict(
        name="lerna:ext",
        **U.run_in(
            "build",
            [
                [*P.HACKED_LABEXTENSION, "build", P.EXT_PACKAGE],
            ],
            file_dep=[
                *P.ALL_CSS,
                *P.ALL_PACKAGE_JSON,
                P.JS_LIB_SCHEMA,
                P.TSBUILDINFO,
                P.YARN_INTEGRITY,
                P.YARN_LOCK,
            ],
            targets=[P.EXT_PACKAGE_JSON],
        ),
    )


def task_dist():
    """prepare release artifacts"""
    if C.DOCS_IN_CI or C.TEST_IN_CI:
        return

    yield dict(
        name="pypi",
        **U.run_in(
            "build",
            [
                [C.PY, "setup.py", "sdist"],
                [C.PY, "setup.py", "bdist_wheel"],
                ["twine", "check", "dist/*.whl", "dist/*.tar.gz"],
            ],
            file_dep=[
                *P.PY_SRC,
                P.README,
                P.LICENSE,
                P.SETUP_CFG,
                P.SETUP_PY,
                P.EXT_PACKAGE_JSON,
            ],
            targets=[P.WHEEL, P.SDIST],
        ),
    )

    for path, tarball in P.NPM_TARBALLS.items():
        yield dict(
            name=f"npm:{path.name}",
            **U.run_in(
                "build",
                [["npm", "pack", path]],
                file_dep=[
                    P.TSBUILDINFO,
                    P.WHEEL,
                    path / "README.md",
                    path / "LICENSE",
                    path / "package.json",
                ],
                targets=[tarball],
                cwd=str(P.DIST),
            ),
        )

    def _run_hash():
        # mimic sha256sum CLI
        if P.SHA256SUMS.exists():
            P.SHA256SUMS.unlink()

        lines = []

        for p in P.HASH_DEPS:
            lines += ["  ".join([sha256(p.read_bytes()).hexdigest(), p.name])]

        output = "\n".join(lines)
        print(output)
        P.SHA256SUMS.write_text(output)

    yield dict(
        name="hash",
        file_dep=P.HASH_DEPS,
        targets=[P.SHA256SUMS],
        actions=[_run_hash],
    )


def task_dev():
    """prepare local development"""
    if C.DOCS_IN_CI or C.TEST_IN_CI:
        return

    yield dict(
        name="pip:install",
        **U.run_in(
            "utest",
            [[*C.INSTALL, "-e", ".", "--ignore-installed", "--no-deps"]],
            file_dep=[P.SETUP_CFG, P.SETUP_PY, P.EXT_PACKAGE_JSON],
        ),
    )

    yield dict(
        name="pip:check",
        task_dep=["dev:pip:install"],
        **U.run_in("utest", [C.FREEZE, C.CHECK], file_dep=[P.SETUP_CFG, P.SETUP_PY]),
    )

    yield dict(
        name="ext:server",
        task_dep=["dev:pip:check"],
        **U.run_in(
            "utest",
            [
                ["jupyter", *app, "enable", "--sys-prefix", "--py", "jupyter_starters"]
                for app in [["serverextension"], ["server", "extension"]]
            ],
            file_dep=[P.SETUP_CFG, P.SETUP_PY],
        ),
    )

    yield dict(
        name="ext:lab",
        task_dep=["dev:pip:check"],
        **U.run_in(
            "utest",
            [[*P.HACKED_LABEXTENSION, "develop", ".", "--overwrite"]],
            file_dep=[
                P.SETUP_CFG,
                P.SETUP_PY,
            ],
        ),
    )


def task_prod():
    if not (C.DOCS_IN_CI or C.TEST_IN_CI):
        return

    yield dict(
        name="pip:install",
        **U.run_in(
            "utest",
            [[*C.INSTALL, P.WHEEL]],
            file_dep=[P.WHEEL],
        ),
    )

    yield dict(
        name="pip:check",
        task_dep=["prod:pip:install"],
        **U.run_in("utest", [C.FREEZE, C.CHECK]),
    )


def task_lab():
    """run JupyterLab "normally" (not watching sources)"""
    if not C.RUNNING_LOCALLY:
        return

    def lab():
        prefix, run_args = U.run_args("docs")
        proc = subprocess.Popen(
            list(map(str, [*run_args, "jupyter", "lab", "--no-browser", "--debug"])),
            stdin=subprocess.PIPE,
        )

        try:
            proc.wait()
        except KeyboardInterrupt:
            print("attempting to stop lab, you may want to check your process monitor")
            proc.terminate()
            proc.communicate(b"y\n")

        proc.wait()
        return True

    return dict(
        uptodate=[lambda: False],
        task_dep=["preflight"],
        actions=[doit.tools.PythonInteractiveAction(lab)],
    )


def task_integrity():
    """ensure integrity of the repo"""
    if C.DOCS_IN_CI or C.TEST_IN_CI:
        return

    yield dict(
        name="all",
        **U.run_in(
            "utest",
            [[*C.PYM, "scripts.integrity"]],
            file_dep=[P.README, P.CHANGELOG, P.SCRIPTS / "integrity.py"],
        ),
    )


def task_preflight():
    """ensure various stages are ready for development"""
    if C.DOCS_IN_CI or C.TEST_IN_CI:
        task_dep = ["prod:pip:check"]
    else:
        task_dep = ["dev:ext:lab", "dev:ext:server"]

    yield dict(
        name="all",
        task_dep=task_dep,
        **U.run_in(
            "utest",
            [[*C.PYM, "scripts.preflight"]],
            file_dep=[P.SCRIPTS / "preflight.py"],
        ),
    )


def task_test():
    """run automated tests"""
    if C.DEMO_IN_BINDER:
        return

    html_utest = P.HTML_UTEST / f"{C.THIS_SUBDIR}-py{C.THIS_PY}.html"
    html_cov = P.HTML_COV / f"{C.THIS_SUBDIR}-py{C.THIS_PY}"
    utest_args = [
        "pytest",
        "-vv",
        "--pyargs",
        "jupyter_starters",
        "--cov=jupyter_starters",
        "--cov-report=term-missing:skip-covered",
        f"--cov-report=html:{html_cov}",
        "--no-cov-on-fail",
        "-p",
        "no:warnings",
        "--html",
        html_utest,
        "--self-contained-html",
        *C.UTEST_ARGS,
    ]

    if C.DOCS_IN_CI or C.TEST_IN_CI:
        task_dep = ["prod:pip:check"]
    else:
        task_dep = ["dev:pip:check"]

    utask = dict(
        name="unit",
        task_dep=task_dep,
        uptodate=[doit.tools.config_changed({"args": str(utest_args)})],
        **U.run_in(
            "utest",
            [utest_args],
            targets=[P.COVERAGE, html_utest, html_cov / "index.html"],
            file_dep=[*P.PY_SRC, P.SETUP_CFG, *P.PY_SCHEMA.glob("*.json")],
        ),
    )

    utask["actions"] = [
        (doit.tools.create_folder, [P.BUILD / "utest"]),
        (U.strip_timestamps, [P.HTML_UTEST]),
        *utask["actions"],
        (U.strip_timestamps, [P.HTML_COV]),
    ]

    yield utask

    task_dep = ["preflight"]

    if not (C.DOCS_IN_CI or C.TEST_IN_CI):
        task_dep += ["lint:rf:rflint"]

    yield dict(
        name="atest",
        task_dep=task_dep,
        file_dep=[*P.ALL_ROBOT, *P.NPM_TARBALLS.values(), P.WHEEL],
        actions=[(U.atest, [])],
        targets=[
            P.ATEST_OUT / f"{C.THIS_ATEST_STEM}-0.robot.xml",
        ],
    )


def task_docs():
    if C.TEST_IN_CI:
        return
    """build documentation"""
    yield dict(
        name="schema",
        **U.run_in(
            "docs",
            [[*C.PYM, "scripts.docs", "--only-schema=1"]],
            file_dep=[P.SCRIPTS / "docs.py", *P.PY_SCHEMA.rglob("*.json")],
            targets=[P.DOCS_SCHEMA_INDEX],
        ),
    )

    if C.DOCS_IN_CI:
        task_dep = ["prod:pip:check"]
    else:
        task_dep = ["dev:pip:check"]

    yield dict(
        name="sphinx",
        task_dep=task_dep,
        **U.run_in(
            "docs",
            [[*C.PYM, "scripts.docs", "--schema=0", "--check-links=0"]],
            file_dep=[
                P.SCRIPTS / "docs.py",
                *P.PY_SRC,
                *P.PY_SCHEMA.rglob("*.json"),
                P.DOCS_SCHEMA_INDEX,
                *P.ALL_DOCS_DEPS,
            ],
            targets=[P.DOCS_INDEX, P.DOCS_BUILDINFO],
        ),
    )

    if not C.DEMO_IN_BINDER:
        yield dict(
            name="check:links",
            **U.run_in(
                "docs",
                [[*C.PYM, "scripts.docs", "--only-check-links=1"]],
                file_dep=[
                    P.SCRIPTS / "docs.py",
                    P.DOCS_SCHEMA_INDEX,
                    P.DOCS_BUILDINFO,
                ],
            ),
        )


def task_watch():
    """watch for live developing"""
    if not C.RUNNING_LOCALLY:
        return

    prefix, run_args = U.run_args("docs")
    yield dict(
        name="lab", uptodate=[lambda: False], actions=[[*run_args, C.JLPM, "watch"]]
    )

    yield dict(
        name="docs", actions=[[*run_args, "sphinx-autobuild", P.DOCS, P.DOCS_OUT]]
    )


class C:
    """constants"""

    SUBDIRS = ["linux-64", "osx-64", "win-64"]
    THIS_SUBDIR = {"Linux": "linux-64", "Darwin": "osx-64", "Windows": "win-64"}[
        platform.system()
    ]
    THIS_PY = "{}.{}".format(*sys.version_info)
    PYTHONS = ["3.6", "3.9"]
    DEFAULT_PY = "3.9"
    DEFAULT_SUBDIR = "linux-64"
    SKIP_LOCKS = bool(json.loads(os.environ.get("SKIP_LOCKS", "1")))
    CI = bool(json.loads(os.environ.get("CI", "0")))
    SKIP_JLPM_IF_CACHED = bool(json.loads(os.environ.get("SKIP_JLPM_IF_CACHED", "1")))
    DOCS_IN_CI = bool(json.loads(os.environ.get("DOCS_IN_CI", "0")))
    TEST_IN_CI = bool(json.loads(os.environ.get("TEST_IN_CI", "0")))
    DEMO_IN_BINDER = bool(json.loads(os.environ.get("DEMO_IN_BINDER", "0")))
    RUNNING_LOCALLY = not CI
    RFLINT_RULES = [
        "LineTooLong:200",
        "TooFewKeywordSteps:0",
        "TooManyTestSteps:30",
    ]
    UTEST_ARGS = safe_load(os.environ.get("UTEST_ARGS", "[]"))
    ATEST_RETRIES = int(os.environ.get("ATEST_RETRIES", "1"))
    ATEST_ARGS = safe_load(os.environ.get("ATEST_ARGS", "[]"))
    THIS_ATEST_STEM = f"{THIS_SUBDIR}-py{THIS_PY}"

    if CI:
        PY = Path(
            shutil.which("python")
            or shutil.which("python3")
            or shutil.which("python.exe")
        ).resolve()
        CONDA = Path(
            shutil.which("conda")
            or shutil.which("conda.exe")
            or shutil.which("conda.cmd")
        ).resolve()
        JLPM = Path(
            shutil.which("jlpm") or shutil.which("jlpm.exe") or shutil.which("jlpm.cmd")
        ).resolve()
    else:
        PY = "python.exe" if THIS_SUBDIR == "win-64" else "python"
        CONDA = "conda"
        JLPM = "jlpm"
    PYM = [PY, "-m"]
    PIP = [*PYM, "pip"]
    INSTALL = [*PIP, "install"]
    FREEZE = [*PIP, "freeze"]
    CHECK = [*PIP, "check"]


class P:
    """paths"""

    DODO = Path(__file__)
    ROOT = DODO.parent
    GITHUB = ROOT / ".github"
    CONDARC = GITHUB / ".condarc"
    SPECS = GITHUB / "specs"
    LOCKS = GITHUB / "locks"
    SCRIPTS = ROOT / "scripts"
    ATEST = ROOT / "atest"
    DOCS = ROOT / "docs"

    SRC = ROOT / "src"
    PY_SRC = sorted(SRC.rglob("*.py"))
    PY_SCRIPTS = sorted(SCRIPTS.rglob("*.py"))
    PY_DOCS = sorted(DOCS.rglob("*.py"))
    PY_ATEST = sorted(ATEST.rglob("*.py"))
    SETUP_CFG = ROOT / "setup.cfg"
    SETUP_PY = ROOT / "setup.py"

    ALL_PY = [DODO, *PY_SRC, *PY_SCRIPTS, *PY_DOCS, *PY_ATEST, SETUP_PY]
    ALL_ROBOT = list(ATEST.rglob("*.robot"))

    YARNRC = ROOT / ".yarnrc"

    PACKAGE_JSON = ROOT / "package.json"
    PACKAGES = ROOT / "packages"
    PACKAGES_JSON = sorted(PACKAGES.glob("*/package.json"))
    EXT_PACKAGE = PACKAGES / "jupyterlab-starters"
    ALL_PACKAGE_JSON = [PACKAGE_JSON, *PACKAGES_JSON]

    DOCS_NOTEBOOKS = sorted(DOCS.rglob("*.ipynb"))
    DOCS_STATIC = [p for p in (DOCS / "_static").rglob("*") if not p.is_dir()]
    DOCS_CONF = DOCS / "conf.py"
    ALL_DOCS_DEPS = [*DOCS_NOTEBOOKS, DOCS_CONF, *DOCS_STATIC]

    # generated but checked in
    YARN_LOCK = ROOT / "yarn.lock"

    # not checked in
    BUILD = ROOT / "build"
    ENVS = ROOT / ".envs"
    DEV_PREFIX = ENVS / "dev"
    DEV_LOCKFILE = LOCKS / f"docs-{C.THIS_SUBDIR}-{C.DEFAULT_PY}.conda.lock"
    DEV_HISTORY = DEV_PREFIX / "conda-meta/history"
    NODE_MODULES = ROOT / "node_modules"
    YARN_INTEGRITY = NODE_MODULES / ".yarn-integrity"
    DIST = ROOT / "dist"
    # TODO: single-source version
    PY_VERSION = "1.0.2a0"
    JS_VERSION = "1.0.2-a0"
    SDIST = DIST / f"jupyter_starters-{PY_VERSION}.tar.gz"
    WHEEL = DIST / f"jupyter_starters-{PY_VERSION}-py3-none-any.whl"
    NPM_TARBALLS = {
        PACKAGES
        / "jupyterlab-starters": DIST
        / f"deathbeds-jupyterlab-starters-{JS_VERSION}.tgz",
        PACKAGES
        / "jupyterlab-rjsf": DIST
        / f"deathbeds-jupyterlab-rjsf-{JS_VERSION}.tgz",
    }
    HASH_DEPS = [SDIST, WHEEL, *NPM_TARBALLS.values()]
    SHA256SUMS = DIST / "SHA256SUMS"
    HTML_UTEST = BUILD / "utest"
    HTML_COV = BUILD / "coverage"
    COVERAGE = ROOT / ".coverage"
    ATEST_OUT = BUILD / "atest"
    DOCS_OUT = BUILD / "docs"
    DOCS_INDEX = DOCS_OUT / "html/index.html"
    DOCS_BUILDINFO = DOCS_OUT / "html/.buildinfo"
    DOCS_SCHEMA_INDEX = DOCS / "schema" / "index.rst"

    # js stuff
    TSBUILDINFO = PACKAGES / "_meta/tsconfig.tsbuildinfo"
    PY_SCHEMA = SRC / "jupyter_starters/schema"
    ALL_PY_SCHEMA = PY_SCHEMA.glob("*.json")
    JS_SRC_SCHEMA_D_TS = PACKAGES / "jupyterlab-starters/src/_schema.d.ts"
    JS_SRC_SCHEMA = PACKAGES / "jupyterlab-starters/src/_schema.json"
    JS_LIB_SCHEMA = PACKAGES / "jupyterlab-starters/lib/_schema.json"
    LABEXT = SRC / "jupyter_starters/labextension"
    EXT_PACKAGE_JSON = LABEXT / "package.json"
    EXT_REMOTE_ENTRY = LABEXT.rglob("remoteEntry*.js")

    # collections of things
    ALL_TSCONFIG = [ROOT / "tsconfigbase.json", *PACKAGES.rglob("src/*/tsconfig.json")]
    ALL_TS = sum(
        (
            [*(p.parent / "src").rglob("*.ts"), *(p.parent / "src").rglob("*.tsx")]
            for p in PACKAGES_JSON
        ),
        [],
    )
    ALL_CSS = sum(
        (
            [*(p.parent / "style").rglob("*.ts"), *(p.parent / "style").rglob("*.css")]
            for p in PACKAGES_JSON
        ),
        [],
    )
    ALL_YAML = [*SPECS.glob("*.yml"), *ROOT.glob("*.yml"), *GITHUB.rglob("*.yml")]
    README = ROOT / "README.md"
    EXAMPLES = ROOT / "examples"
    CHANGELOG = ROOT / "CHANGELOG.md"
    LICENSE = ROOT / "LICENSE"
    ALL_MD = [*ROOT.glob("*.md")]
    ALL_JSON = [
        *ALL_PACKAGE_JSON,
        *ROOT.glob("*.json"),
        *ATEST.rglob("*.json"),
        *ALL_PY_SCHEMA,
    ]
    ALL_PRETTIER = [*ALL_TS, *ALL_JSON, *ALL_CSS, *ALL_YAML]
    ALL_IPYNB = [
        p
        for p in [*DOCS.rglob("*.ipynb"), *EXAMPLES.rglob("*.ipynb")]
        if "checkpoints" not in str(p)
    ]

    HACKED_LABEXTENSION = [C.PY, SCRIPTS / "hacked-labextension.py"]


class D:
    """data"""


class U:
    """utilities"""

    @classmethod
    def cmd(cls, *args, **kwargs):
        if "shell" not in kwargs:
            kwargs["shell"] = False
        return doit.tools.CmdAction(*args, **kwargs)

    @classmethod
    def run_args(cls, env=None):
        if C.RUNNING_LOCALLY:
            env = "dev"
            prefix = P.ENVS / env

        if C.CI:
            prefix = Path(os.environ["CONDA_PREFIX"])

        run_args = [
            C.CONDA,
            "run",
            "--prefix",
            prefix,
            "--live-stream",
            "--no-capture-output",
        ]
        return prefix, run_args

    @classmethod
    def run_in(cls, env, actions, **kwargs):
        prefix, run_args = U.run_args(env)
        history = prefix / "conda-meta/history"
        file_dep = kwargs.pop("file_dep", [])
        targets = kwargs.pop("targets", [])
        return dict(
            file_dep=[history, *file_dep],
            actions=[U.cmd([*run_args, *action], **kwargs) for action in actions],
            targets=targets,
        )

    @classmethod
    def lock(cls, env_name, py, subdir, extra_env_names=None, include_base=True):
        extra_env_names = extra_env_names or []
        args = ["conda-lock", "--mamba", "--platform", subdir, "-c", "conda-forge"]
        stem = f"{env_name}-{subdir}-{py}"
        lockfile = P.LOCKS / f"{stem}.conda.lock"

        specs = []

        if include_base:
            specs += [P.SPECS / "_base.yml"]

        for env in [env_name, *extra_env_names]:
            for fname in [f"{env}", f"py{py}", f"{env}-{subdir}"]:
                spec = P.SPECS / f"{fname}.yml"
                if spec.exists():
                    specs += [spec]

        args += sum([["--file", spec] for spec in specs], [])
        args += [
            "--filename-template",
            env_name + "-{platform}-" + f"{py}.conda.lock",
        ]
        return dict(
            name=f"""{py}:{subdir}:{env_name}""",
            file_dep=specs,
            actions=[
                (doit.tools.create_folder, [P.LOCKS]),
                U.cmd(args, cwd=str(P.LOCKS)),
            ],
            targets=[lockfile],
        )

    RE_TIMESTAMPS = [
        r"\d{4}-\d{2}-\d{2} \d{2}:\d{2} -\d*",
        r"\d+-[^\-]{3}-\d{4} at \d{2}:\d{2}:\d{2}",
    ]

    @classmethod
    def strip_timestamps(cls, root):
        paths = root.rglob("*.html") if root.is_dir() else [root]
        for path in paths:
            text = path.read_text(encoding="utf-8")
            for pattern in U.RE_TIMESTAMPS:
                if not re.findall(pattern, text):
                    continue

                path.write_text(
                    re.sub(
                        pattern,
                        "TIMESTAMP",
                        text,
                    )
                )

    @classmethod
    def atest(cls):
        return_code = 1
        for attempt in range(C.ATEST_RETRIES + 1):
            return_code = U.atest_attempt(attempt)
            if return_code == 0:
                break
        U.rebot()
        return return_code == 0

    @classmethod
    def atest_attempt(cls, attempt):
        prefix, run_args = U.run_args("atest")
        extra_args = []
        stem = f"{C.THIS_ATEST_STEM}-{attempt}"
        out_dir = P.ATEST_OUT / stem

        if out_dir.exists():
            try:
                shutil.rmtree(out_dir)
            except Exception as err:
                print(err)

        out_dir.mkdir(parents=True, exist_ok=True)

        if attempt:
            extra_args += ["--loglevel", "TRACE"]
            previous = P.ATEST_OUT / f"{C.THIS_ATEST_STEM}-{attempt - 1}.robot.xml"
            if previous.exists():
                extra_args += ["--rerunfailed", str(previous)]

        extra_args += C.ATEST_ARGS

        variables = dict(
            ATTEMPT=attempt,
            NAME=C.THIS_ATEST_STEM,
            OS=platform.system(),
            Py=C.THIS_PY,
        )

        extra_args += sum(
            [["--variable", f"{key}:{value}"] for key, value in variables.items()], []
        )

        args = [
            "--name",
            C.THIS_ATEST_STEM,
            "--outputdir",
            out_dir,
            "--output",
            P.ATEST_OUT / f"{stem}.robot.xml",
            "--log",
            P.ATEST_OUT / f"{stem}.log.html",
            "--report",
            P.ATEST_OUT / f"{stem}.report.html",
            "--xunit",
            P.ATEST_OUT / f"{stem}.xunit.xml",
            "--randomize",
            "all",
            *extra_args,
            # the folder must always go last
            P.ATEST,
        ]

        str_args = [*map(str, [*run_args, *C.PYM, "robot", *args])]
        print(">>>", " ".join(str_args))
        proc = subprocess.Popen(str_args, cwd=P.ATEST)

        try:
            return proc.wait()
        except KeyboardInterrupt:
            proc.kill()
            return 1

    @classmethod
    def rebot(cls):
        prefix, run_args = U.run_args("atest")
        args = [
            *run_args,
            C.PY,
            "-m",
            "robot.rebot",
            "--name",
            "🤖",
            "--nostatusrc",
            "--merge",
            "--output",
            P.ATEST_OUT / "robot.xml",
            "--log",
            P.ATEST_OUT / "log.html",
            "--report",
            P.ATEST_OUT / "report.html",
            "--xunit",
            P.ATEST_OUT / "xunit.xml",
        ] + sorted(P.ATEST_OUT.glob("*.robot.xml"))

        str_args = [*map(str, args)]

        print(">>> rebot args:", " ".join(str_args))

        proc = subprocess.Popen(str_args)

        try:
            return proc.wait()
        except KeyboardInterrupt:
            proc.kill()
            return 1


class R(doit.reporter.ConsoleReporter):
    """fancy reporter"""

    TIMEFMT = "%H:%M:%S"
    SKIP = " " * len(TIMEFMT)
    _timings = {}  # type: typing.Dict[str, datetime]
    ISTOP = "🛑"
    ISTART = "🐛"
    ISKIP = "⏩"
    IPASS = "🦋"

    def execute_task(self, task):
        start = datetime.now()
        title = task.title()
        self._timings[title] = [start]
        self.outstream.write(
            f"""{R.ISTART} {start.strftime(R.TIMEFMT)}   START  {title}\n"""
        )

    def outtro(self, task, emoji, status):
        title = task.title()
        start, end = self._timings[title] = [
            *self._timings.get(title, []),
            datetime.now(),
        ]
        delta = end - start
        sec = str(delta.seconds).rjust(7)
        self.outstream.write(f"{emoji}  {sec}s   {status}  {task.title()}\n")

    def add_failure(self, task, exception):
        super().add_failure(task, exception)
        self.outtro(task, R.ISTOP, "FAIL")

    def add_success(self, task):
        super().add_success(task)
        self.outtro(task, R.IPASS, "PASS")

    def skip_uptodate(self, task):
        self.outstream.write(f"{R.ISKIP} {R.SKIP}    SKIP      {task.title()}\n")

    skip_ignore = skip_uptodate


DOIT_CONFIG = {
    "backend": "sqlite3",
    "verbosity": 2,
    "par_type": "thread",
    "reporter": R,
    "default_tasks": ["lint", "integrity", "test", "docs"],
}

# patch environment for all child tasks
os.environ.update(
    CONDARC=str(P.CONDARC),
    MAMBA_NO_BANNER="1",
    PYTHONUNBUFFERED="1",
    PYTHONIOENCODING="utf-8",
)

try:
    # for windows, mostly, but whatever
    import colorama

    colorama.init()
except ImportError:
    pass
