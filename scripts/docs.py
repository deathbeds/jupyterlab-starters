""" antidisinformationarianism
"""
import re
import shutil
import sys
from pathlib import Path
from subprocess import check_call

import jinja2

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

SKIPS = "not github and not ujson"


def fix_schema_md():
    """ fix up generated markdown to work (somewhat better) with sphinx
    """
    (SCHEMA_DOCS / "README.md").unlink()
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


def docs():
    """ build docs
    """
    shutil.rmtree(DOCS_BUILD, ignore_errors=1)
    shutil.rmtree(SCHEMA_DOCS, ignore_errors=1)
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
    check_call(["sphinx-build", "-M", "html", DOCS, DOCS_BUILD])
    fix_schema_html()
    check_call(["pytest", "--check-links", DOCS_BUILD, "-k", SKIPS])

    return 0


if __name__ == "__main__":
    sys.exit(docs())
