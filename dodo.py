"""development automation for jupyter[lab]-starter"""
import difflib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import typing
from datetime import datetime
from hashlib import sha256
from pathlib import Path

import doit.reporter
import doit.tools
from ruamel.yaml import safe_load
from ruamel.yaml.main import safe_dump


class C:
    """constants"""

    SUBDIRS = ["linux-64", "osx-64", "win-64"]
    THIS_SUBDIR = {"Linux": "linux-64", "Darwin": "osx-64", "Windows": "win-64"}[
        platform.system()
    ]
    THIS_PY = "{}.{}".format(*sys.version_info)
    PYTHONS = ["3.8", "3.11"]
    DEFAULT_PY = PYTHONS[-1]
    EXPLICIT = "@EXPLICIT"
    PIP_LOCK_LINE = "# pip "
    UTF8 = dict(encoding="utf-8")
    JSON_FMT = dict(indent=2, sort_keys=True)
    DEFAULT_SUBDIR = "linux-64"
    SKIP_LOCKS = bool(json.loads(os.environ.get("SKIP_LOCKS", "1")))
    CI = bool(json.loads(os.environ.get("CI", "0")))
    RTD = os.environ.get("READTHEDOCS") == "True"
    SKIP_JLPM_IF_CACHED = bool(json.loads(os.environ.get("SKIP_JLPM_IF_CACHED", "0")))
    DOCS_IN_CI = bool(json.loads(os.environ.get("DOCS_IN_CI", "0")))
    TEST_IN_CI = bool(json.loads(os.environ.get("TEST_IN_CI", "0")))
    DOCS_OR_TEST_IN_CI = DOCS_IN_CI or TEST_IN_CI
    DEMO_IN_BINDER = bool(json.loads(os.environ.get("DEMO_IN_BINDER", "0")))
    RUNNING_LOCALLY = not CI
    ROBOCOP_RULES = [
        # "LineTooLong:200",
        # "TooFewKeywordSteps:0",
        # "TooManyTestSteps:30",
        *("--configure", "empty-lines-between-sections:empty_lines:2"),
        *("--configure", "too-many-calls-in-test-case:max_calls:18"),
        *("--configure", "too-long-test-case:max_len:22"),
        *("--exclude", "if-can-be-used"),
        *("--exclude", "if-can-be-merged"),
    ]
    UTEST_ARGS = safe_load(os.environ.get("UTEST_ARGS", "[]"))
    ATEST_RETRIES = int(os.environ.get("ATEST_RETRIES", "1"))
    ATEST_ARGS = safe_load(os.environ.get("ATEST_ARGS", "[]"))
    ATEST_PROCESSES = safe_load(os.environ.get("ATEST_PROCESSES", "4"))
    THIS_ATEST_STEM = f"{THIS_SUBDIR}-py{THIS_PY}"
    LAB_ARGS = safe_load(os.environ.get("LAB_ARGS", '["--no-browser", "--debug"]'))
    YARN_REGISTRY = "https://registry.npmjs.org/"

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
    LERNA = [JLPM, "lerna"]
    INSTALL = [*PIP, "install"]
    FREEZE = [*PIP, "freeze"]
    CHECK = [*PIP, "check"]
    LITE_SPEC = ["jupyterlite==0.1.0b18"]


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
    LITE = ROOT / "lite"
    BINDER = ROOT / ".binder"

    SRC = ROOT / "src"
    PY_SRC = sorted(SRC.rglob("*.py"))
    PY_SCRIPTS = sorted(SCRIPTS.rglob("*.py"))
    PY_DOCS = sorted(DOCS.rglob("*.py"))
    PY_ATEST = sorted(ATEST.rglob("*.py"))
    SETUP_CFG = ROOT / "setup.cfg"
    SETUP_PY = ROOT / "setup.py"

    ALL_PY = [DODO, *PY_SRC, *PY_SCRIPTS, *PY_DOCS, *PY_ATEST, SETUP_PY]
    ALL_ROBOT = [*ATEST.rglob("*.robot"), *ATEST.rglob("*.resource")]

    YARNRC = ROOT / ".yarnrc"

    PACKAGE_JSON = ROOT / "package.json"
    PACKAGES = ROOT / "packages"
    PACKAGES_JSON = sorted(PACKAGES.glob("*/package.json"))
    EXT_PACKAGE = PACKAGES / "jupyterlab-starters"
    EXT_SCHEMA = EXT_PACKAGE / "schema"
    EXT_SETTINGS_SCHEMA = EXT_SCHEMA / "settings-provider.json"
    ALL_PACKAGE_JSON = [PACKAGE_JSON, *PACKAGES_JSON]
    ALL_PLUGIN_SCHEMA = [EXT_SETTINGS_SCHEMA]

    LITE_BUILD_CONFIG = LITE / "jupyter_lite_config.json"
    LITE_OVERRIDES = LITE / "overrides.json"
    ALL_LITE_CONFIG = LITE.glob("*.json")

    RTD_ENV = DOCS / "rtd.yml"
    DOCS_NOTEBOOKS = sorted(DOCS.rglob("*.ipynb"))
    DOCS_STATIC = [
        p
        for p in (DOCS / "_static").rglob("*")
        if not p.is_dir() and p.parent.name not in ("schema", "_")
    ]
    DOCS_CONF = DOCS / "conf.py"
    ALL_DOCS_DEPS = [*DOCS_NOTEBOOKS, DOCS_CONF, *DOCS_STATIC]

    # generated but checked in
    YARN_LOCK = ROOT / "yarn.lock"

    # not checked in
    BUILD = ROOT / "build"
    LITE_SHA256SUMS = BUILD / "docs-app/SHA256SUMS"
    ENVS = ROOT / ".envs"
    DEV_PREFIX = ENVS / "dev"
    DEV_LOCKFILE = LOCKS / f"docs-{C.THIS_SUBDIR}-{C.DEFAULT_PY}.conda.lock"
    DEV_HISTORY = DEV_PREFIX / "conda-meta/history"
    NODE_MODULES = ROOT / "node_modules"
    YARN_INTEGRITY = NODE_MODULES / ".yarn-integrity"
    DIST = ROOT / "dist"
    # TODO: single-source version
    PY_VERSION = "2.0.0"
    JS_VERSION = "2.0.0"
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
    COVERAGE = BUILD / "coverage"
    ATEST_OUT = BUILD / "atest"
    DOCS_OUT = BUILD / "docs"
    DOCS_OUT_HTML = DOCS_OUT / "html"
    DOCS_INDEX = DOCS_OUT_HTML / "index.html"
    DOCS_BUILDINFO = DOCS_OUT_HTML / ".buildinfo"
    DOCS_SCHEMA_INDEX = DOCS / "schema" / "index.md"

    # js stuff
    TSBUILDINFO = PACKAGES / "_meta/.src.tsbuildinfo"
    PY_SCHEMA = SRC / "jupyter_starters/schema"
    PY_SCHEMA_V3 = PY_SCHEMA / "v3.json"
    ALL_PY_SCHEMA = PY_SCHEMA.glob("*.json")
    JS_SRC_SCHEMA_D_TS = PACKAGES / "jupyterlab-starters/src/_schema.d.ts"
    JS_SRC_SCHEMA = PACKAGES / "jupyterlab-starters/src/_schema.json"
    JS_LIB_SCHEMA = PACKAGES / "jupyterlab-starters/lib/_schema.json"
    LABEXT = SRC / "jupyter_starters/labextension"
    EXT_PACKAGE_JSON = LABEXT / "package.json"
    EXT_REMOTE_ENTRY = LABEXT.rglob("remoteEntry*.js")
    PRETTIER_CACHE = BUILD / ".prettier-cache"

    # collections of things
    ALL_TSCONFIG = [ROOT / "tsconfigbase.json", *PACKAGES.rglob("src/*/tsconfig.json")]
    ALL_TS = sum(
        (
            [*(p.parent / "src").rglob("*.ts"), *(p.parent / "src").rglob("*.tsx")]
            for p in PACKAGES_JSON
        ),
        [],
    )
    ALL_SRC_CSS = sum(
        [[*(p.parent / "style").rglob("*.css")] for p in PACKAGES_JSON], []
    )
    ALL_CSS = [
        *ALL_SRC_CSS,
        *DOCS.rglob("_static/**/*.css"),
    ]
    ALL_YAML = [
        *SPECS.glob("*.yml"),
        *ROOT.glob("*.yml"),
        *GITHUB.rglob("*.yml"),
        *DOCS.glob("*.yml"),
    ]
    README = ROOT / "README.md"
    EXAMPLES = ROOT / "examples"
    CHANGELOG = ROOT / "CHANGELOG.md"
    LICENSE = ROOT / "LICENSE"
    PRETTIER_CFG = [ROOT / ".prettierignore"]
    ALL_MD = [*ROOT.glob("*.md"), *GITHUB.rglob("*.md"), *PACKAGES.glob("*/README.md")]
    ALL_JS = [ROOT / ".eslintrc.js"]
    ALL_JSON = [
        *ALL_PACKAGE_JSON,
        *LITE.glob("*.json"),
        *BINDER.glob("*.json"),
        *ROOT.glob("*.json"),
        *ATEST.rglob("*.json"),
        *ALL_PY_SCHEMA,
        *ALL_PLUGIN_SCHEMA,
    ]
    ALL_PRETTIER = [*ALL_TS, *ALL_JSON, *ALL_CSS, *ALL_YAML, *ALL_MD, *ALL_JS]
    ALL_IPYNB = [
        p
        for p in [*DOCS.rglob("*.ipynb"), *EXAMPLES.rglob("*.ipynb")]
        if "checkpoints" not in str(p)
    ]

    DEMO_SERVER_CFG = ROOT / "jupyter_server_config.json"
    DEMO_NOTEBOOK_CFG = ROOT / "jupyter_notebook_config.json"

    # binder
    BINDER_OVERRIDES = BINDER / "overrides.json"
    PREFIX_SETTINGS = (
        Path(sys.prefix) if C.CI or C.DEMO_IN_BINDER else DEV_PREFIX
    ) / "share/jupyter/lab/settings"
    PREFIX_OVERRIDES = PREFIX_SETTINGS / BINDER_OVERRIDES.name


class U:
    """utilities"""

    RE_TIMESTAMPS = [
        r"\d{4}-\d{2}-\d{2} \d{2}:\d{2} -\d*",
        r"\d+-[^\-]{3}-\d{4} at \d{2}:\d{2}:\d{2}",
    ]

    def cmd(*args, **kwargs):
        if "shell" not in kwargs:
            kwargs["shell"] = False
        return doit.tools.CmdAction(*args, **kwargs)

    def run_args(env=None):
        conda_prefix = Path(os.environ.get("CONDA_PREFIX", sys.prefix))

        if C.RUNNING_LOCALLY:
            env = "dev"
            prefix = P.ENVS / env

        if C.CI or C.DEMO_IN_BINDER or C.RTD:
            prefix = conda_prefix

        if prefix == conda_prefix:
            run_args = []
        else:
            run_args = [
                C.CONDA,
                "run",
                "--prefix",
                prefix,
                "--live-stream",
                "--no-capture-output",
            ]
        return prefix, run_args

    def run_in(env, actions, **kwargs):
        prefix, run_args = U.run_args(env)
        history = prefix / "conda-meta/history"
        file_dep = kwargs.pop("file_dep", [])
        targets = kwargs.pop("targets", [])
        return dict(
            file_dep=[history, *file_dep],
            actions=[
                action
                if callable(action) or callable(action[0])
                else U.cmd([*run_args, *action], **kwargs)
                for action in actions
            ],
            targets=targets,
        )

    def lock(env_name, py, subdir, extra_env_names=None, include_base=True):
        extra_env_names = extra_env_names or []
        args = [
            "conda-lock",
            "--mamba",
            "--platform",
            subdir,
            "-c",
            "conda-forge",
            "--kind",
            "explicit",
        ]
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
                (U._lock_one, [lockfile, args, specs]),
            ],
            targets=[lockfile],
        )

    def _lock_one(lockfile, args, specs):
        new_header = U._lock_header(specs)
        if lockfile.exists():
            old_header = lockfile.read_text().split(C.EXPLICIT)[0].strip()
            if new_header == old_header:
                print(f"\t\t...  {lockfile.name} is up-to-date", flush=True)
                return True

            print(
                "\n".join(
                    difflib.unified_diff(
                        old_header.splitlines(),
                        new_header.splitlines(),
                        lockfile.name,
                        "new",
                    )
                ),
                flush=True,
            )

        if not shutil.which("conda-lock"):
            print("conda-lock is not available")
            return False

        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            subprocess.check_call([*map(str, args)], cwd=td)
            new_body = (tdp / lockfile.name).read_text(**C.UTF8).split(C.EXPLICIT)[1]

        lockfile.write_text("\n".join([new_header, C.EXPLICIT, new_body.strip(), ""]))

    def _lock_header(specs):
        norm_specs = {}
        for spec in specs:
            spec_data = safe_load(spec.read_text(**C.UTF8))
            spec_data["dependencies"] = [
                dep.strip().lower() if isinstance(dep, str) else dep
                for dep in sorted(
                    spec_data["dependencies"],
                    key=lambda a: a if isinstance(a, str) else "zzzzzzzzzzzz",
                )
            ]
            norm_specs[spec.name] = spec_data

        raw = json.dumps(norm_specs, **C.JSON_FMT)
        return textwrap.indent(raw, "# ").strip()

    def lock_to_env(lockfile, env_file):
        def _update():
            lock_text = lockfile.read_text(**C.UTF8)
            lock_lines = lock_text.split(C.EXPLICIT)[1].strip().splitlines()

            pip_lines = [
                line for line in lock_lines if line.startswith(C.PIP_LOCK_LINE)
            ]
            not_pip_lines = [
                line for line in lock_lines if not line.startswith(C.PIP_LOCK_LINE)
            ]

            if pip_lines:
                not_pip_lines += [
                    {"pip": [line.split("@")[1].strip() for line in pip_lines]}
                ]

            env = {
                "name": "readthedocs",
                "channels": ["conda-forge", "nodefaults"],
                "dependencies": not_pip_lines,
            }
            env_file.write_text(safe_dump(env, default_flow_style=False))

        rel = env_file.relative_to(P.ROOT)
        stem = lockfile.stem.rsplit(".", 1)[0]

        task = dict(
            name=f"{rel}:{stem}",
            **U.run_in(
                "docs",
                actions=[[C.JLPM, "prettier", "--write", env_file]],
                targets=[env_file],
                file_dep=[lockfile, P.YARN_INTEGRITY],
            ),
        )

        task["actions"] = [_update, *task["actions"]]

        yield task

    def strip_timestamps(root):
        paths = root.rglob("*.html") if root.is_dir() else [root]
        for path in paths:
            text = path.read_text(**C.UTF8)
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

    def atest():
        return_code = 1
        for attempt in range(C.ATEST_RETRIES + 1):
            return_code = U.atest_attempt(attempt)
            if return_code == 0:
                break
        U.rebot()
        return return_code == 0

    def atest_attempt(attempt):
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
            previous = P.ATEST_OUT / f"{C.THIS_ATEST_STEM}-{attempt - 1}/output.xml"
            if previous.exists():
                extra_args += ["--rerunfailed", str(previous)]

        extra_args += C.ATEST_ARGS

        variables = dict(
            ATTEMPT=attempt,
            NAME=C.THIS_ATEST_STEM,
            OS=platform.system(),
            Py=C.THIS_PY,
            ROOT=P.ROOT,
        )

        extra_args += sum(
            [["--variable", f"{key}:{value}"] for key, value in variables.items()], []
        )

        pabot_args = [
            *("--processes", C.ATEST_PROCESSES),
            *("--artifacts", "png,log,txt,ipynb"),
            "--artifactsinsubfolders",
        ]

        args = [
            *("--name", C.THIS_ATEST_STEM),
            *("--outputdir", out_dir),
            *("--log", out_dir / "log.html"),
            *("--report", out_dir / "report.html"),
            *("--xunit", out_dir / "xunit.xml"),
            *("--randomize", "all"),
            *extra_args,
            # the folder must always go last
            P.ATEST,
        ]

        str_args = [*map(str, [*run_args, "pabot", *pabot_args, *args])]
        print(">>>", " ".join(str_args))
        proc = subprocess.Popen(str_args, cwd=P.ATEST)

        try:
            return proc.wait()
        except KeyboardInterrupt:
            proc.kill()
            return 1

    def rebot():
        prefix, run_args = U.run_args("atest")
        args = [
            *run_args,
            C.PY,
            "-m",
            "robot.rebot",
            "--nostatusrc",
            "--merge",
            *("--name", "🤖"),
            *("--output", P.ATEST_OUT / "output.xml"),
            *("--log", P.ATEST_OUT / "log.html"),
            *("--report", P.ATEST_OUT / "report.html"),
            *("--xunit", P.ATEST_OUT / "xunit.xml"),
        ] + sorted(P.ATEST_OUT.glob("*/output.xml"))

        str_args = [*map(str, args)]

        print(">>> rebot args:", " ".join(str_args))

        proc = subprocess.Popen(str_args)

        try:
            return proc.wait()
        except KeyboardInterrupt:
            proc.kill()
            return 1

    def patch_plugin_schema():
        plugin_schema = json.load(P.EXT_SETTINGS_SCHEMA.open())
        py_schema = json.load(P.PY_SCHEMA_V3.open())

        plugin_schema["definitions"] = py_schema["definitions"]

        P.EXT_SETTINGS_SCHEMA.write_text(
            json.dumps(plugin_schema, **C.JSON_FMT), **C.UTF8
        )

    def patch_overrides(src: Path, dest: Path):
        if not dest.parent.exists():
            dest.parent.mkdir(parents=True)

        old_data = {} if not dest.exists() else json.load(dest.open())
        new_data = dict(**old_data)
        new_data.update(json.load(src.open()))

        new_data_text = json.dumps(new_data, indent=2, sort_keys=True)
        old_data_text = json.dumps(old_data, indent=2, sort_keys=True)

        if new_data_text != old_data_text:
            dest.write_text(new_data_text)

    def normalize_json(path):
        path.write_text(
            json.dumps(json.loads(path.read_text(**C.UTF8)), **C.JSON_FMT) + "\n",
            **C.UTF8,
        )

    def clean_some(*paths):
        for path in paths:
            if path.is_dir():
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()


def task_lock():
    """generate conda locks for all envs"""
    if C.CI or C.DEMO_IN_BINDER or C.RTD:
        return

    yield U.lock("build", C.DEFAULT_PY, C.DEFAULT_SUBDIR, ["node", "lab", "lint"])
    yield U.lock(
        "binder",
        C.DEFAULT_PY,
        C.DEFAULT_SUBDIR,
        ["run", "build", "lab", "node", "docs"],
    )

    for subdir in C.SUBDIRS:
        for py in C.PYTHONS:
            yield U.lock("atest", py, subdir, ["run", "lab", "utest"])

        yield U.lock("lock", C.DEFAULT_PY, subdir)
        yield U.lock(
            "docs",
            C.DEFAULT_PY,
            subdir,
            ["node", "build", "lint", "atest", "utest", "lab", "run"],
        )

    yield U.lock_to_env(P.LOCKS / f"docs-linux-64-{C.DEFAULT_PY}.conda.lock", P.RTD_ENV)


def task_env():
    if C.CI or C.DEMO_IN_BINDER:
        return

    yield dict(
        name="dev",
        file_dep=[P.DEV_LOCKFILE],
        actions=[
            ["mamba", "create", "--prefix", P.DEV_PREFIX, "--file", P.DEV_LOCKFILE],
        ],
        targets=[P.DEV_HISTORY],
    )


def task_lint():
    """improve and ensure code quality"""
    if C.DOCS_OR_TEST_IN_CI or C.DEMO_IN_BINDER:
        return

    yield dict(
        name="py:isort:black",
        **U.run_in(
            "docs",
            [
                [*C.PYM, "ssort", *P.ALL_PY],
                [*C.PYM, "isort", *P.ALL_PY],
                [*C.PYM, "black", "--quiet", *P.ALL_PY],
            ],
            file_dep=[*P.ALL_PY],
        ),
    )

    for linter, file_dep_cmd in {
        "pyflakes": [P.ALL_PY, [*C.PYM, "pyflakes"]],
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
            [[*C.PYM, "robotidy", *P.ALL_ROBOT]],
            file_dep=P.ALL_ROBOT,
        ),
    )

    robocop = [*C.PYM, "robocop", *C.ROBOCOP_RULES]

    yield dict(
        name="rf:robocop",
        task_dep=["lint:rf:tidy"],
        **U.run_in("docs", [robocop + P.ALL_ROBOT], file_dep=P.ALL_ROBOT),
    )

    for pkg_json in P.ALL_PACKAGE_JSON:
        yield dict(
            name=f"prettier-package-json:{pkg_json.relative_to(P.ROOT)}",
            **U.run_in(
                "docs",
                [[C.JLPM, "prettier-package-json", "--write", pkg_json]],
                file_dep=[pkg_json, P.YARN_INTEGRITY],
            ),
        )
    prettier = [C.JLPM, "prettier"] + (
        ["--write", "--list-different"] if C.RUNNING_LOCALLY else ["--check"]
    )

    if C.RUNNING_LOCALLY:
        for json_path in P.ALL_JSON:
            if json_path in P.ALL_PACKAGE_JSON:
                continue
            yield dict(
                name=f"json:{json_path.relative_to(P.ROOT)}",
                **U.run_in(
                    "docs",
                    [
                        (U.normalize_json, [json_path]),
                        [C.JLPM, "prettier", "--write", json_path],
                    ],
                    file_dep=[json_path, P.YARN_INTEGRITY],
                ),
            )
    rel_prettier = [p.relative_to(P.ROOT) for p in P.ALL_PRETTIER]

    yield dict(
        name="prettier",
        **U.run_in(
            "docs",
            [
                [
                    *prettier,
                    "--cache",
                    f"--cache-location={P.PRETTIER_CACHE}",
                    *rel_prettier,
                ]
            ],
            file_dep=[
                P.YARN_INTEGRITY,
                *P.PRETTIER_CFG,
                *[p for p in P.ALL_PRETTIER if not p.name.startswith("_")],
            ],
        ),
    )

    eslint = [C.JLPM, "eslint", "--cache", "--ext", ".js,.jsx,.ts,.tsx"] + (
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

    stylelint = [C.JLPM, "stylelint", "--cache"] + (
        ["--fix"] if C.RUNNING_LOCALLY else []
    )

    yield dict(
        name="stylelint",
        task_dep=["lint:prettier"],
        **U.run_in(
            "docs",
            [[*stylelint, *P.ALL_CSS]],
            file_dep=[
                P.YARN_INTEGRITY,
                *P.ALL_CSS,
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
    jlpm_args = ["--registry", C.YARN_REGISTRY]
    jlpm_args += ["--frozen-lockfile"] if C.CI else []

    actions = [[*C.LERNA, "bootstrap"]]

    if not C.CI:
        actions += [[C.JLPM, "deduplicate"]]

    if C.DOCS_OR_TEST_IN_CI:
        print("nothing to do with jlpm for docs/test in ci")
        return

    if not (C.SKIP_JLPM_IF_CACHED and P.YARN_INTEGRITY.exists()):
        actions = [[C.JLPM, *jlpm_args], *actions]

    yield dict(
        name="install",
        **U.run_in(
            "build",
            actions,
            file_dep=[P.YARNRC, *P.ALL_PACKAGE_JSON],
            targets=[P.YARN_INTEGRITY],
        ),
    )


def task_build():
    """build intermediate artifacts"""
    if C.DOCS_OR_TEST_IN_CI:
        return

    yield dict(
        name="lerna:pre",
        **U.run_in(
            "build",
            [
                [*C.LERNA, "bootstrap"],
                U.patch_plugin_schema,
                [*C.LERNA, "run", "--stream", "build:pre"],
                [
                    C.JLPM,
                    "prettier",
                    "--write",
                    P.JS_SRC_SCHEMA,
                    P.JS_LIB_SCHEMA,
                    P.JS_SRC_SCHEMA_D_TS,
                    P.EXT_SETTINGS_SCHEMA,
                ],
            ],
            file_dep=[
                P.YARN_INTEGRITY,
                *P.ALL_PY_SCHEMA,
                *P.ALL_PACKAGE_JSON,
                P.YARN_LOCK,
            ],
            targets=[
                P.JS_SRC_SCHEMA,
                P.JS_LIB_SCHEMA,
                P.JS_SRC_SCHEMA_D_TS,
                P.EXT_SETTINGS_SCHEMA,
            ],
        ),
    )

    yield dict(
        name="lerna:lib",
        **U.run_in(
            "build",
            [[*C.LERNA, "run", "--stream", "build"]],
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
                ["jupyter", "labextension", "build", P.EXT_PACKAGE],
            ],
            file_dep=[
                *P.ALL_SRC_CSS,
                *P.ALL_PACKAGE_JSON,
                *P.ALL_PLUGIN_SCHEMA,
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
    if C.DOCS_OR_TEST_IN_CI:
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


class D:
    """data"""

    def pip_specs():
        env_spec = (P.RTD_ENV).read_text(**C.UTF8)
        pip_deps = [
            p for p in safe_load(env_spec)["dependencies"] if isinstance(p, dict)
        ]
        if pip_deps:
            return pip_deps[0]["pip"]
        return []


def task_dev():
    """prepare local development"""
    if C.DOCS_OR_TEST_IN_CI:
        return

    extra_pip_args = ["--ignore-installed", "--no-deps"]

    pip_actions = [[*C.INSTALL, "-e", ".", *extra_pip_args]]

    pip_specs = D.pip_specs()

    if pip_specs:
        pip_actions += [[*C.INSTALL, *pip_specs, *extra_pip_args]]

    yield dict(
        name="pip:install",
        **U.run_in(
            "utest",
            pip_actions,
            file_dep=[P.SETUP_CFG, P.SETUP_PY, P.EXT_PACKAGE_JSON],
        ),
    )

    yield dict(
        name="pip:check",
        task_dep=["dev:pip:install"],
        **U.run_in(
            "utest",
            [
                C.FREEZE,
                *([] if C.RTD else [C.CHECK]),
            ],
            file_dep=[P.SETUP_CFG, P.SETUP_PY],
        ),
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
            [["jupyter", "labextension", "develop", ".", "--overwrite"]],
            file_dep=[P.SETUP_CFG, P.SETUP_PY, *P.ALL_PLUGIN_SCHEMA],
        ),
    )

    for dest in [P.PREFIX_OVERRIDES, P.LITE_OVERRIDES]:
        yield dict(
            name=f"ext:lab:overrides:{dest.parent.name}",
            file_dep=[P.BINDER_OVERRIDES],
            task_dep=["dev:pip:check"],
            targets=[dest],
            actions=[
                (U.patch_overrides, [P.BINDER_OVERRIDES, dest]),
            ],
        )


def task_prod():
    if not C.DOCS_OR_TEST_IN_CI:
        return

    yield dict(
        name="pip:install",
        **U.run_in(
            "utest",
            [[*C.INSTALL, P.WHEEL, *D.pip_specs()]],
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
            list(map(str, [*run_args, "jupyter", "lab", *C.LAB_ARGS])),
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
    if C.DOCS_OR_TEST_IN_CI:
        return

    yield dict(
        name="all",
        **U.run_in(
            "utest",
            [[*C.PYM, "scripts.integrity"]],
            file_dep=[
                P.README,
                P.CHANGELOG,
                *P.ALL_TSCONFIG,
                *P.ALL_PACKAGE_JSON,
                P.SCRIPTS / "integrity.py",
            ],
        ),
    )


def task_preflight():
    """ensure various stages are ready for development"""
    file_dep = [P.SCRIPTS / "preflight.py"]
    if C.DOCS_OR_TEST_IN_CI:
        task_dep = ["prod:pip:check"]
    else:
        task_dep = ["dev:ext:lab", "dev:ext:server"]
        file_dep += [P.PREFIX_OVERRIDES]

    yield dict(
        name="all",
        task_dep=task_dep,
        **U.run_in(
            "utest",
            [[*C.PYM, "scripts.preflight"]],
            file_dep=file_dep,
        ),
    )


def task_test():
    """run automated tests"""
    if C.DEMO_IN_BINDER:
        return

    html_utest = P.HTML_UTEST / f"{C.THIS_SUBDIR}-py{C.THIS_PY}.html"
    cov_data = P.COVERAGE / f"{C.THIS_SUBDIR}-py{C.THIS_PY}.pytest.coverage"
    utest_args = [
        "coverage",
        "run",
        f"--data-file={cov_data}",
        "--branch",
        "--context=pytest",
        "--source=jupyter_starters",
        "-m",
        "pytest",
        "-vv",
        "--pyargs",
        "jupyter_starters",
        "--script-launch-mode=subprocess",
        "-p",
        "no:warnings",
        "--html",
        html_utest,
        "--self-contained-html",
        *C.UTEST_ARGS,
    ]

    if C.DOCS_OR_TEST_IN_CI:
        task_dep = ["prod:pip:check"]
    else:
        task_dep = ["dev:pip:check"]

    utask = dict(
        name="unit",
        task_dep=task_dep,
        uptodate=[doit.tools.config_changed({"args": str(utest_args)})],
        **U.run_in(
            "utest",
            [(U.clean_some, [cov_data]), utest_args],
            targets=[html_utest, cov_data],
            file_dep=[*P.PY_SRC, P.SETUP_CFG, *P.PY_SCHEMA.glob("*.json")],
        ),
    )

    utask["actions"] = [
        (doit.tools.create_folder, [P.BUILD / "utest"]),
        (U.strip_timestamps, [P.HTML_UTEST]),
        *utask["actions"],
    ]

    yield utask

    task_dep = ["preflight"]

    if not (C.DOCS_OR_TEST_IN_CI):
        task_dep += ["lint:rf:robocop"]

    yield dict(
        name="atest",
        task_dep=task_dep,
        file_dep=[*P.ALL_ROBOT, *P.NPM_TARBALLS.values(), P.WHEEL, P.LITE_SHA256SUMS],
        actions=[(U.atest, [])],
        targets=[P.ATEST_OUT / "output.xml", P.ATEST_OUT / "log.html"],
    )


def task_lite():
    if C.DOCS_OR_TEST_IN_CI:
        task_dep = ["prod:pip:check"]
    else:
        task_dep = ["dev:pip:check"]

    yield dict(
        name="install",
        **U.run_in(
            "docs",
            [
                [*C.PIP, "install", "--no-deps", *C.LITE_SPEC],
            ],
        ),
    )

    yield dict(
        name="build",
        task_dep=[*task_dep, "lite:install"],
        **U.run_in(
            "docs",
            [
                ["jupyter-lite", "build"],
                [
                    "jupyter-lite",
                    "doit",
                    "--",
                    "run",
                    "pre_archive:report:SHA256SUMS",
                ],
            ],
            file_dep=[*P.ALL_LITE_CONFIG],
            targets=[P.LITE_SHA256SUMS],
            cwd=P.LITE,
        ),
    )


def task_docs():
    """build documentation"""

    if C.TEST_IN_CI:
        return

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
                *P.ALL_DOCS_DEPS,
                *P.PY_SCHEMA.rglob("*.json"),
                *P.PY_SRC,
                P.DOCS_SCHEMA_INDEX,
                P.LITE_SHA256SUMS,
                P.SCRIPTS / "docs.py",
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

    yield dict(
        name="binder:conf",
        file_dep=[P.DEMO_SERVER_CFG],
        targets=[P.DEMO_NOTEBOOK_CFG],
        actions=[
            lambda: [
                P.DEMO_NOTEBOOK_CFG.unlink(),
                shutil.copy2(P.DEMO_SERVER_CFG, P.DEMO_NOTEBOOK_CFG),
                None,
            ][-1]
        ],
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
        name="docs", actions=[[*run_args, "sphinx-autobuild", P.DOCS, P.DOCS_OUT_HTML]]
    )


class R(doit.reporter.ConsoleReporter):
    """fancy reporter"""

    TIMEFMT = "%H:%M:%S"
    SKIP = " " * len(TIMEFMT)
    _timings: typing.Dict[str, datetime] = {}
    ISTOP = "🛑"
    ISTART = "🐛"
    ISKIP = "⏩"
    IPASS = "🦋"

    def skip_uptodate(self, task):
        self.outstream.write(f"{R.ISKIP} {R.SKIP}    SKIP      {task.title()}\n")

    skip_ignore = skip_uptodate

    def execute_task(self, task):
        start = datetime.now()
        title = task.title()
        self._timings[title] = [start]
        self.outstream.write(
            f"""{R.ISTART} {start.strftime(R.TIMEFMT)}   START  {title}\n"""
        )

    def outtro(self, task, emoji, status):
        title = task.title()
        sec = "???"
        try:
            start, end = self._timings[title] = [
                *self._timings.get(title, []),
                datetime.now(),
            ]
            delta = end - start
            sec = str(delta.seconds).rjust(7)
        except Exception:
            pass
        self.outstream.write(f"{emoji}  {sec}s   {status}  {task.title()}\n")

    def add_failure(self, task, exception):
        super().add_failure(task, exception)
        self.outtro(task, R.ISTOP, "FAIL")

    def add_success(self, task):
        super().add_success(task)
        self.outtro(task, R.IPASS, "PASS")


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
    PYTHONIOENCODING=C.UTF8["encoding"],
)

try:
    # for windows, mostly, but whatever
    import colorama

    colorama.init()
except ImportError:
    pass
