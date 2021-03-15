"""development automation for jupyter[lab]-starter"""
# pylint: disable=invalid-name,too-many-arguments,import-error
# pylint: disable=too-few-public-methods,missing-function-docstring
import json
import os
import platform
import typing
from datetime import datetime
from pathlib import Path

import doit.reporter
import doit.tools


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
            "docs", [["isort", *P.ALL_PY], ["black", *P.ALL_PY]], file_dep=[*P.ALL_PY]
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

    yield dict(
        name="prettier",
        **U.run_in(
            "docs",
            [["jlpm", "prettier", "--list-different", "--write", *P.ALL_PRETTIER]],
            file_dep=[P.YARN_INTEGRITY, *P.ALL_PRETTIER],
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


def task_dist():
    """prepare release artifacts"""


def task_lab():
    """run jupyterlab"""


def task_integrity():
    """ensure integrity of the repo"""


def task_preflight():
    """ensure various stages are ready for development"""

    yield dict(name="lab", actions=[["echo", "TODO"]])


def task_test():
    """run automated tests"""


def task_docs():
    """build documentation"""


class C:
    """constants"""

    SUBDIRS = ["linux-64", "osx-64", "win-64"]
    THIS_SUBDIR = {"Linux": "linux-64", "Darwin": "osx-64", "Windows": "win-64"}[
        platform.system()
    ]
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

    PY_SRC = sorted((ROOT / "src").rglob("*.py"))
    PY_SCRIPTS = sorted((ROOT / "scripts").rglob("*.py"))
    PY_DOCS = sorted((ROOT / "docs").rglob("*.py"))
    PY_ATEST = sorted((ROOT / "atest").rglob("*.py"))

    ALL_PY = [DODO, *PY_SRC, *PY_SCRIPTS, *PY_DOCS, *PY_ATEST]
    ALL_ROBOT = list((ROOT / "atest").rglob("*.robot"))

    SETUP_CFG = ROOT / "setup.cfg"

    YARNRC = ROOT / ".yarnrc"

    PACKAGE_JSON = ROOT / "package.json"
    PACKAGES = ROOT / "packages"
    PACKAGES_JSON = sorted(PACKAGES.glob("*/package.json"))
    ALL_PACKAGE_JSON = [PACKAGE_JSON, *PACKAGES_JSON]

    # generated but checked in
    YARN_LOCK = ROOT / "yarn.lock"

    # not checked in
    ENVS = ROOT / ".envs"
    DEV_PREFIX = ENVS / "dev"
    DEV_LOCKFILE = LOCKS / f"docs-{C.THIS_SUBDIR}-{C.DEFAULT_PY}.conda.lock"
    DEV_HISTORY = DEV_PREFIX / "conda-meta/history"
    NODE_MODULES = ROOT / "node_modules"
    YARN_INTEGRITY = NODE_MODULES / ".yarn-integrity"

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
    ALL_MD = [*ROOT.glob("*.md")]
    ALL_JSON = [*ALL_PACKAGE_JSON, *ROOT.glob("*.json"), *ATEST.rglob("*.json")]
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
        return dict(
            file_dep=[history, *file_dep],
            actions=[
                U.cmd(
                    [
                        "conda",
                        "run",
                        "--prefix",
                        prefix,
                        "--no-capture-output",
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
