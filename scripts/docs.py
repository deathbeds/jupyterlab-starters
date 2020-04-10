""" antidisinformationarianism
"""
import os
import re
import shutil
import sys
from pathlib import Path
from subprocess import call, check_call
from tempfile import TemporaryDirectory

import jinja2

HAS_PYTEST = False

try:
    import pytest_check_links

    print("pytest_check_links available, will check links", pytest_check_links)
    HAS_PYTEST = True
except ImportError as err:
    print("pytest_check_links not available, skipping link check", err)


SPHINX_STAGE = os.environ.get("STARTERS_SPHINX_STAGE")

SETUP = SPHINX_STAGE == "setup"
FINISHED = SPHINX_STAGE == "build-finished"
META = SPHINX_STAGE is None

RST_TEMPLATE = jinja2.Template(
    """
All JSON Schema
===============

.. toctree::
    :maxdepth: 1

    {% for path in paths %}{{ path.name.replace('.md', '') }}
    {% endfor %}
"""
)

ROOT = Path(__file__).parent.parent
SCHEMA_SRC = ROOT / "src" / "jupyter_starters" / "schema"
DOCS = ROOT / "docs"
DOCS_BUILD = DOCS / "_build"
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


def fix_schema_md():
    """ fix up generated markdown to work (somewhat better) with sphinx
    """
    if SCHEMA_README.exists():
        SCHEMA_README.unlink()

    md_files = list(SCHEMA_DOCS.glob("*.md"))

    check_call(["jlpm", "prettier", "--write", "--loglevel", "silent", *md_files])

    for md_file in md_files:
        md_txt = md_file.read_text()

        for pattern, replacement in MD_REPLACEMENTS:
            md_txt = re.sub(pattern, replacement, md_txt, flags=re.M)

        md_file.write_text(md_txt)

    check_call(["jlpm", "prettier", "--write", "--loglevel", "silent", *md_files])


def fix_schema_html():
    """ fix up generated HTML
    """
    html_files = list((DOCS_BUILD / "schema").glob("*.html"))

    for html_file in html_files:
        html_txt = html_file.read_text()

        for pattern, replacement in HTML_REPLACEMENTS:
            html_txt = re.sub(pattern, replacement, html_txt, flags=re.M)

        html_file.write_text(html_txt)


def make_schema_index():
    """ make an index for all the schema markdown
    """
    md_files = sorted(SCHEMA_DOCS.glob("*.md"))
    index = SCHEMA_DOCS / "index.rst"

    rst = RST_TEMPLATE.render(paths=md_files)
    index.write_text(rst)


def check_links():
    """ check local links with pytest-check-links in a clean directory
    """
    ini = CHECK_INI.format(extra_k="")
    # do this in a temporary directory to avoid surprises

    with TemporaryDirectory() as tmp:
        tdp = Path(tmp)
        dest = tdp / "a" / "deep" / "path"
        dest.parent.mkdir(parents=True)
        shutil.copytree(DOCS / "_build" / "html", dest)
        (dest / "pytest.ini").write_text(ini)

        return call(["pytest"], cwd=dest)


def docs():
    """ build (and test) docs.

        because readthedocs, this gets called twice from inside sphinx
    """

    if META:
        shutil.rmtree(DOCS_BUILD, ignore_errors=1)
        shutil.rmtree(SCHEMA_DOCS, ignore_errors=1)
        check_call(["sphinx-build", "-M", "html", DOCS, DOCS_BUILD])
        if HAS_PYTEST:
            check_links()
    elif SETUP and not SCHEMA_DOCS.exists():
        check_call(["jlpm"])
        check_call(
            [
                "jlpm",
                "jsonschema2md",
                "-x",
                "docs/schema/raw",
                "-d",
                SCHEMA_SRC,
                "-e",
                "json",
                "-o",
                SCHEMA_DOCS,
            ]
        )
        fix_schema_md()
        make_schema_index()
    elif FINISHED:
        fix_schema_html()

    return 0


if __name__ == "__main__":
    sys.exit(docs())
