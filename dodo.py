"""development automation for jupyter[lab]-starter"""
# pylint: disable=invalid-name,too-many-arguments,import-error
# pylint: disable=too-few-public-methods,missing-function-docstring
import json
import os
import platform
import re
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
    for subdir in C.SUBDIRS:
        for py in C.PYTHONS:
            yield U.lock("utest", py, subdir, ["run", "lab"])
        yield U.lock("build", C.DEFAULT_PY, subdir, ["node", "lab"])
        yield U.lock("atest", C.DEFAULT_PY, subdir)
        yield U.lock(
            "docs",
            C.DEFAULT_PY,
            subdir,
            ["node", "build", "lint", "atest", "utest", "lab", "run"],
        )
        if subdir == "linux-64":
            yield U.lock("binder", C.DEFAULT_PY, subdir, ["run", "lab"])


def task_env():
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
    yield dict(
        name="py:isort:black",
        **U.run_in(
            "docs",
            [["isort", *P.ALL_PY], ["black", "--quiet", *P.ALL_PY]],
            file_dep=[*P.ALL_PY],
        ),
    )

    for file_dep, linter in [
        [P.ALL_PY, ["flake8"]],
        [P.PY_SRC, ["pylint", "--reports", "n", "--score", "n"]],
        [P.PY_SRC, ["mypy", "--no-error-summary", "--config-file", P.SETUP_CFG]],
    ]:
        yield dict(
            name=f"py:{linter[0]}",
            task_dep=["lint:py:isort:black"],
            **U.run_in("docs", [linter + file_dep], file_dep=[P.SETUP_CFG, *file_dep]),
        )

    yield dict(
        name="rf:tidy",
        **U.run_in(
            "docs",
            [["python", "-m", "robot.tidy", "--inplace", *P.ALL_ROBOT]],
            file_dep=P.ALL_ROBOT,
        ),
    )

    rflint = ["rflint", *sum([["--configure", rule] for rule in C.RFLINT_RULES], [])]

    yield dict(
        name="rf:rflint",
        task_dep=["lint:rf:tidy"],
        **U.run_in("docs", [rflint + P.ALL_ROBOT], file_dep=P.ALL_ROBOT),
    )

    prettier = ["jlpm", "prettier"] + (
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

    eslint = ["jlpm", "eslint", "--ext", ".js,.jsx,.ts,.tsx"] + (
        ["--fix"] if C.RUNNING_LOCALLY else []
    )

    yield dict(
        name="eslint",
        task_dep=["lint:prettier"],
        **U.run_in(
            "docs",
            [[*eslint, P.PACKAGES]],
            file_dep=[P.YARN_INTEGRITY, *P.ALL_TS, *P.ROOT.glob(".eslint*")],
        ),
    )


def task_jlpm():
    yield dict(
        name="install",
        **U.run_in(
            "build",
            [["jlpm"]],
            file_dep=[P.YARNRC, *P.ALL_PACKAGE_JSON],
            targets=[P.YARN_INTEGRITY],
        ),
    )


def task_build():
    """build intermediate artifacts"""
    yield dict(
        name="lerna:pre",
        **U.run_in(
            "build",
            [
                ["jlpm", "lerna", "run", "--stream", "build:pre"],
                [
                    "jlpm",
                    "prettier",
                    "--write",
                    P.JS_SRC_SCHEMA,
                    P.JS_LIB_SCHEMA,
                    P.JS_SRC_SCHEMA_D_TS,
                ],
            ],
            file_dep=[P.YARN_INTEGRITY, *P.ALL_PY_SCHEMA, *P.ALL_PACKAGE_JSON],
            targets=[P.JS_SRC_SCHEMA, P.JS_LIB_SCHEMA, P.JS_SRC_SCHEMA_D_TS],
        ),
    )

    yield dict(
        name="lerna:lib",
        **U.run_in(
            "build",
            [
                ["jlpm", "lerna", "run", "--stream", "build"],
            ],
            file_dep=[
                P.YARN_INTEGRITY,
                P.JS_SRC_SCHEMA,
                P.JS_SRC_SCHEMA_D_TS,
                *P.ALL_TS,
                *P.ALL_PACKAGE_JSON,
                *P.ALL_TSCONFIG,
            ],
            targets=[P.TSBUILDINFO],
        ),
    )

    yield dict(
        name="lerna:ext",
        **U.run_in(
            "build",
            [
                ["jlpm", "lerna", "run", "--stream", "build:ext"],
            ],
            file_dep=[
                P.YARN_INTEGRITY,
                P.TSBUILDINFO,
                P.JS_LIB_SCHEMA,
                *P.ALL_PACKAGE_JSON,
                *P.ALL_CSS,
            ],
            targets=[P.EXT_PACKAGE_JSON],
        ),
    )


def task_dist():
    """prepare release artifacts"""
    yield dict(
        name="pypi",
        **U.run_in(
            "build",
            [
                ["python", "setup.py", "sdist"],
                ["python", "setup.py", "bdist_wheel"],
                ["twine", "check", "dist/*"],
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
                    path / "README.md",
                    path / "LICENSE",
                    path / "package.json",
                ],
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
    pip = ["python", "-m", "pip"]
    install = [*pip, "install", "-e", ".", "--ignore-installed", "--no-deps"]
    freeze = [*pip, "freeze"]
    check = [*pip, "check"]
    yield dict(
        name="pip:install",
        **U.run_in("utest", [install], file_dep=[P.SETUP_CFG, P.SETUP_PY]),
    )

    yield dict(
        name="pip:check",
        task_dep=["dev:pip:install"],
        **U.run_in("utest", [freeze, check], file_dep=[P.SETUP_CFG, P.SETUP_PY]),
    )


def task_lab():
    """run jupyterlab"""


def task_integrity():
    """ensure integrity of the repo"""


def task_preflight():
    """ensure various stages are ready for development"""

    yield dict(name="lab", actions=[["echo", "TODO"]])


def task_test():
    """run automated tests"""
    html_utest = P.HTML_UTEST / f"{C.THIS_SUBDIR}-py{C.THIS_PY}.html"
    html_cov = P.HTML_COV / f"{C.THIS_SUBDIR}-py{C.THIS_PY}"
    utest_args = [
        "pytest",
        "--pyargs",
        "jupyter_starters",
        "--cov=jupyter_starters",
        "--cov-report=term-missing:skip-covered",
        f"--cov-report=html:{html_cov}",
        "--no-cov-on-fail",
        "-p",
        "no:warnings",
        "--flake8",
        "--black",
        "--mypy",
        "--html",
        html_utest,
        "--self-contained-html",
        *C.UTEST_ARGS,
    ]
    utask = dict(
        name="unit",
        task_dep=["dev:pip:install"],
        uptodate=[doit.tools.config_changed({"args": str(utest_args)})],
        **U.run_in(
            "utest",
            [utest_args],
            targets=[P.COVERAGE, html_utest, html_cov / "index.html"],
            file_dep=[*P.PY_SRC, P.SETUP_CFG, *P.PY_SCHEMA.glob("*.json")],
        ),
    )

    utask["actions"] = [
        (U.strip_timestamps, [P.HTML_UTEST]),
        *utask["actions"],
        (U.strip_timestamps, [P.HTML_COV]),
    ]

    yield utask


def task_docs():
    """build documentation"""


class C:
    """constants"""

    SUBDIRS = ["linux-64", "osx-64", "win-64"]
    THIS_SUBDIR = {"Linux": "linux-64", "Darwin": "osx-64", "Windows": "win-64"}[
        platform.system()
    ]
    THIS_PY = "{}.{}".format(*sys.version_info)
    PYTHONS = ["3.6", "3.9"]
    DEFAULT_PY = "3.9"
    SKIP_LOCKS = bool(json.loads(os.environ.get("SKIP_LOCKS", "1")))
    CI = bool(json.loads(os.environ.get("CI", "0")))
    RUNNING_LOCALLY = not CI
    RFLINT_RULES = [
        "LineTooLong:200",
        "TooFewKeywordSteps:0",
        "TooManyTestSteps:30",
    ]
    UTEST_ARGS = safe_load(os.environ.get("UTEST_ARGS", "[]"))


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
    ALL_PACKAGE_JSON = [PACKAGE_JSON, *PACKAGES_JSON]

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
    PY_VERSION = "1.0.0a0"
    JS_VERSION = "1.0.0-a0"
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

    # js stuff
    TSBUILDINFO = PACKAGES / "_meta/tsconfig.tsbuildinfo"
    PY_SCHEMA = SRC / "jupyter_starters/schema"
    ALL_PY_SCHEMA = PY_SCHEMA.glob("*.json")
    JS_SRC_SCHEMA_D_TS = PACKAGES / "jupyterlab-starters/src/_schema.d.ts"
    JS_SRC_SCHEMA = PACKAGES / "jupyterlab-starters/src/_schema.json"
    JS_LIB_SCHEMA = PACKAGES / "jupyterlab-starters/lib/_schema.json"
    LABEXT = SRC / "jupyter_starters/labextension"
    EXT_PACKAGE_JSON = LABEXT / "package.json"

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
    LICENSE = ROOT / "LICENSE"
    ALL_MD = [*ROOT.glob("*.md")]
    ALL_JSON = [
        *ALL_PACKAGE_JSON,
        *ROOT.glob("*.json"),
        *ATEST.rglob("*.json"),
        *ALL_PY_SCHEMA,
    ]
    ALL_PRETTIER = [*ALL_TS, *ALL_JSON, *ALL_CSS, *ALL_YAML]


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
    def run_in(cls, env, actions, **kwargs):
        if C.RUNNING_LOCALLY:
            env = "dev"
        prefix = P.ENVS / env
        history = prefix / "conda-meta/history"
        file_dep = kwargs.pop("file_dep", [])
        targets = kwargs.pop("targets", [])
        run_args = [
            "conda",
            "run",
            "--prefix",
            prefix,
            "--live-stream",
            "--no-capture-output",
        ]
        return dict(
            file_dep=[history, *file_dep],
            actions=[
                U.cmd(
                    [
                        *run_args,
                        *action,
                    ],
                    **kwargs,
                )
                for action in actions
            ],
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
            *self._timings[title],
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
    "default_tasks": ["preflight:lab"],
    "reporter": R,
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
