"""development automation for jupyter[lab]-starter"""

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


DOIT_CONFIG = {
    "backend": "sqlite3",
    "verbosity": 2,
    "par_type": "thread",
    "default_tasks": ["preflight:lab"],
    "reporter": U.Reporter,
}
