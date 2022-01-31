""" antidisinformationarianism
"""
import os
import re
import shutil
import sys
from argparse import ArgumentParser
from pathlib import Path
from subprocess import call, check_call
from tempfile import TemporaryDirectory

import jinja2

HAS_PYTEST = False

try:
    __import__("pytest_check_links")
    HAS_PYTEST = True
except (AttributeError, ImportError):
    pass

SPHINX_STAGE = os.environ.get("STARTERS_SPHINX_STAGE")

SETUP = SPHINX_STAGE == "setup"
FINISHED = SPHINX_STAGE == "build-finished"
META = SPHINX_STAGE is None

INDEX_TEMPLATE = jinja2.Template(
    """
# All JSON Schema

```{toctree}
:maxdepth: 1

{% for path in paths %}{{ path.name.replace('.md', '') }}
{% endfor %}
```
""".strip()
)

ROOT = Path(__file__).parent.parent
NODE_MODULES = ROOT / "node_modules"
SCHEMA_SRC = ROOT / "src" / "jupyter_starters" / "schema"
DOCS = ROOT / "docs"
BUILD = ROOT / "build"
DOCS_BUILD = BUILD / "docs"
SCHEMA_DOCS = DOCS / "schema"
RGH = "https://raw.githubusercontent.com"
SCHEMA_STEM = f"{RGH}/deathbeds/jupyterlab-starters/master/src/jupyter_starters/schema/"

MD_REPLACEMENTS = [
    # avoid lexer warnings
    [r"^```(txt|regexp)", "```"],
    # fix header level
    [r"^(#+) ", r"\1## "],
    # defined in not useful
    [r"^\s*- defined in: \[.*?\]\(.*?\)", ""],
    [r"\| Defined (by|In)", ""],
    [r"\[(Jupyter Starters JSON|v\d+.json)\]\(.*?\)", ""],
    # $id not useful
    [re.escape(SCHEMA_STEM), ""],
    # regexpr not useful
    [r"\[try pattern\]\(.*?\)", ""],
]

HTML_REPLACEMENTS = [
    # dangling links to markdown are bad
    [r'"(.*?)\.md"', r'"\1.html"'],
]

SCHEMA_README = SCHEMA_DOCS / "README.md"

CHECK_INI = """
[pytest]
junit_family = xunit2
addopts =
    --check-links
    -k "not ipynb and not http and not ujson {extra_k}"
filterwarnings =
    ignore::PendingDeprecationWarning
    ignore::DeprecationWarning
"""


def make_parser():
    parser = ArgumentParser("docs")
    parser.add_argument("--check-links", default=True)
    parser.add_argument("--only-check-links", default=False)
    parser.add_argument("--schema", default=True)
    parser.add_argument("--only-schema", default=False)
    return parser


def make_schema_docs() -> int:
    if not NODE_MODULES.exists():
        check_call(["jlpm", "--frozen-lockfile"])
    check_call(
        [
            "jlpm",
            "jsonschema2md",
            "-x",
            "docs/_static/schema",
            "-d",
            SCHEMA_SRC,
            "-e",
            "json",
            "-o",
            SCHEMA_DOCS,
        ]
    )
    fix_schema_md()
    return make_schema_index()


def fix_schema_md():
    """fix up generated markdown to work (somewhat better) with sphinx"""
    if SCHEMA_README.exists():
        SCHEMA_README.unlink()

    md_files = list(SCHEMA_DOCS.glob("*.md"))
    prettier = ["jlpm", "--silent", "prettier", "--write", "--loglevel", "silent"]

    check_call([*prettier, *md_files])

    for md_file in md_files:
        md_txt = md_file.read_text()

        for pattern, replacement in MD_REPLACEMENTS:
            md_txt = re.sub(pattern, replacement, md_txt, flags=re.M)

        md_file.write_text(md_txt)

    check_call([*prettier, *md_files])


def fix_schema_html() -> int:
    """fix up generated HTML"""
    html_files = list((DOCS_BUILD / "schema").glob("*.html"))

    for html_file in html_files:
        html_txt = html_file.read_text()

        for pattern, replacement in HTML_REPLACEMENTS:
            html_txt = re.sub(pattern, replacement, html_txt, flags=re.M)

        html_file.write_text(html_txt)

    return 0


def make_schema_index() -> int:
    """make an index for all the schema markdown"""
    md_files = sorted(SCHEMA_DOCS.glob("*.md"))
    index = SCHEMA_DOCS / "index.rst"

    index_text = INDEX_TEMPLATE.render(paths=md_files)
    index.write_text(index_text)
    return 0


def run_check_links() -> int:
    """check local links with pytest-check-links in a clean directory"""
    ini = CHECK_INI.format(extra_k="")
    # do this in a temporary directory to avoid surprises

    with TemporaryDirectory() as tmp:
        tdp = Path(tmp)
        dest = tdp / "a" / "deep" / "path"
        dest.parent.mkdir(parents=True)
        shutil.copytree(DOCS_BUILD / "html", dest)
        (dest / "pytest.ini").write_text(ini)

        return call(["pytest"], cwd=dest)


def docs(check_links=True, schema=True, only_schema=False, only_check_links=False):
    """build (and test) docs.

    because readthedocs, this gets called twice from inside sphinx
    """
    if only_check_links:
        return run_check_links()

    if only_schema:
        shutil.rmtree(SCHEMA_DOCS, ignore_errors=1)
        return make_schema_docs()

    if META:
        shutil.rmtree(DOCS_BUILD, ignore_errors=1)
        if schema:
            shutil.rmtree(SCHEMA_DOCS, ignore_errors=1)
        return call(["sphinx-build", "-M", "html", DOCS, DOCS_BUILD])

    if SETUP and not SCHEMA_DOCS.exists():
        return make_schema_docs()

    if FINISHED:
        return fix_schema_html()


if __name__ == "__main__":
    sys.exit(docs(**dict(vars(make_parser().parse_args()))))
