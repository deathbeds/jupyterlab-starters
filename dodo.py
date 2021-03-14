"""development automation for jupyter[lab]-starter"""
import os
from datetime import datetime
import doit.reporter

from pathlib import Path


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

class P:
    """paths"""
    DODO = Path(__file__)
    ROOT = DODO.parent
    GITHUB = ROOT / ".github"
    CONDARC = GITHUB / ".condarc"


class D:
    """data"""


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
