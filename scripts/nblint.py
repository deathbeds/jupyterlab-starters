"""Linter and formatter of notebooks."""
import shutil
import subprocess
import sys
from pathlib import Path

import black
import nbformat
from isort.api import sort_code_string

HERE = Path(__file__).parent
ROOT = HERE.parent

NODE = Path(
    shutil.which("node") or shutil.which("node.exe") or shutil.which("node.cmd")
).resolve()
NODE_MODULES = ROOT / "node_modules"
PRETTIER = [NODE, NODE_MODULES / ".bin/prettier"]

NB_METADATA_KEYS = ["kernelspec", "language_info", "jupyter_starters"]


def blacken(source):
    """Apply black to a source string."""
    return black.format_str(source, mode=black.FileMode(line_length=88))


def nblint_one(nb_node):
    """Format/lint one notebook."""
    changes = 0
    has_empty = 0
    nb_metadata_keys = list(nb_node.metadata.keys())
    for key in nb_metadata_keys:
        if key not in NB_METADATA_KEYS:
            nb_node.metadata.pop(key)
    for cell in nb_node.cells:
        cell_type = cell["cell_type"]
        source = "".join(cell["source"])
        if not source.strip():
            has_empty += 1
        if cell_type == "markdown":
            args = [
                *PRETTIER,
                "--stdin-filepath",
                "foo.md",
                "--prose-wrap",
                "always",
            ]
            prettier = subprocess.Popen(
                list(map(str, args)),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
            out, _err = prettier.communicate(source.encode("utf-8"))
            new = out.decode("utf-8").rstrip()
            if new != source:
                cell["source"] = new.splitlines(True)
                changes += 1
        elif cell_type == "code":
            if cell["outputs"] or cell["execution_count"]:
                cell["outputs"] = []
                cell["execution_count"] = None
                changes += 1
            if [line for line in source.splitlines() if line.strip().startswith("!")]:
                continue
            if source.startswith("%"):
                continue
            new = sort_code_string(source)
            new = blacken(new).rstrip()
            if new != source:
                cell["source"] = new.splitlines(True)
                changes += 1

    if has_empty:
        changes += 1
        nb_node.cells = [
            cell for cell in nb_node.cells if "".join(cell["source"]).strip()
        ]

    return nb_node


def nblint(nb_paths):
    """Lint a number of notebook paths."""
    len_paths = len(nb_paths)

    for i, nb_path in enumerate(nb_paths):
        nb_text = nb_path.read_text(encoding="utf-8")

        if len_paths > 1:
            print(f"[{i + 1} of {len_paths}] {nb_path}", flush=True)

        nb_node = nblint_one(nbformat.reads(nb_text, 4))

        with nb_path.open("w", encoding="utf-8") as fpt:
            nbformat.write(nb_node, fpt)

    return 0


if __name__ == "__main__":
    sys.exit(nblint([Path(p) for p in sys.argv[1:]]))
