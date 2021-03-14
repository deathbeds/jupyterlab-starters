"""development automation for jupyter[lab]-starter"""
import os
import json
from datetime import datetime
import doit.reporter
import doit.tools

from pathlib import Path


def task_lock():
    if C.SKIP_LOCKS:
        return
    """generate conda locks for all envs"""
    for subdir in C.SUBDIRS:
        for py in C.PYTHONS:
            yield U.lock(f"run", py, subdir)
        yield U.lock("build", C.DEFAULT_PY, subdir)
        yield U.lock("atest", C.DEFAULT_PY, subdir)
        yield U.lock("lint", C.DEFAULT_PY, subdir)
        yield U.lock("docs", C.DEFAULT_PY, subdir, ["build", "lint", "atest"])

def task_lint():
    """improve and ensure code quality"""

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

    yield dict(
        name="lab",
        actions=[["echo", "TODO"]]
    )

def task_test():
    """run automated tests"""

def task_docs():
    """build documentation"""

class C:
    """constants"""
    SUBDIRS = ["linux-64", "osx-64", "win-64"]
    PYTHONS = ["3.6", "3.9"]
    DEFAULT_PY = "3.9"
    SKIP_LOCKS = bool(json.loads(os.environ.get("SKIP_LOCKS", "1")))

class P:
    """paths"""
    DODO = Path(__file__)
    ROOT = DODO.parent
    GITHUB = ROOT / ".github"
    CONDARC = GITHUB / ".condarc"
    SPECS = GITHUB / "specs"
    LOCKS = GITHUB / "locks"
    SCRIPTS = ROOT / "scripts"


class D:
    """data"""

class U:
    """utilities"""
    cmd = lambda *args, **kwargs: doit.tools.CmdAction(*args, **kwargs, shell=False)
    script = lambda *args, **kwargs: U.cmd(*args, **kwargs, cwd=str(P.SCRIPTS))

    @classmethod
    def lock(cls, env_name, py, subdir, extra_env_names=[], include_base=True):
        args = ["conda-lock", "--mamba", "--platform", subdir]
        stem = f"{env_name}-{subdir}-{py}"
        lockfile = P.LOCKS / f"{stem}.conda.lock"

        specs = []

        if include_base:
            specs += [P.SPECS / "_base.yml"]

        for env in [env_name, *extra_env_names]:
            for fname in [f"{env}", f"{env}-{subdir}", f"{env}-{subdir}-{py}"]:
                spec = P.SPECS / f"{fname}.yml"
                if spec.exists():
                    specs += [spec]

        args += sum([["--file", spec] for spec in specs], [])
        args += [
            "--filename-template",
            env_name + "-{platform}-" + f"{py}.conda.lock",
        ]
        return dict(
            name=f"""{env_name}:{py}:{subdir}""",
            file_dep=specs,
            actions=[
                (doit.tools.create_folder, [P.LOCKS]),
                U.cmd(args, cwd=str(P.LOCKS)),
            ],
            targets=[lockfile],
        )


class R(doit.reporter.ConsoleReporter):
    TIMEFMT = "%H:%M:%S"
    SKIP = " " * len(TIMEFMT)
    _timings = {}
    ISTOP = "🛑"
    ISTART = "🐛"
    ISKIP = "⏩"
    IPASS = "🦋"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
