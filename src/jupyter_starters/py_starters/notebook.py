""" use a notebook as a starter
"""
import tempfile
from collections import defaultdict
from pathlib import Path
from unittest.mock import patch

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from notebook.utils import url_path_join as ujoin

from .._json import JsonSchemaException, json_validator, loads

NBFORMAT_KEY = "jupyter_starters"


def response_from_notebook(src, manager):
    """ load a path and return the metadata
    """
    nbp = Path(src).resolve()
    nbjson = loads(nbp.read_text())
    return response_from_nbjson(nbjson)


def response_from_nbjson(nbjson):
    """ get the starter response
    """
    return nbjson.get("metadata", {}).get(NBFORMAT_KEY, {})


def starter_from_nbjson(nbjson):
    """ get just the starter
    """
    return response_from_nbjson(nbjson).get("starter", {})


async def notebook_starter(name, starter, path, body, manager):
    """ (re)runs a notebook until its schema is correct
    """
    nbp = Path(starter["src"]).resolve()
    nbjson = nbp.read_text()
    notebook_node = nbformat.reads(nbjson, as_version=4)
    notebook_node.metadata.jupyter_starters.body = body
    kernel_name = notebook_node.metadata.kernelspec.name
    executor = ExecutePreprocessor(timeout=600, kernel_name=kernel_name)

    fake_env = defaultdict(str)

    with tempfile.TemporaryDirectory() as tmpdir:
        tdp = Path(tmpdir)
        tmp_nb = tdp / "_starter.ipynb"
        tmp_nb.write_text(nbformat.writes(notebook_node))
        fake_env["STARTER_NOTEBOOK"] = str(tmp_nb)

        with patch("os.environ", fake_env):
            executor.preprocess(notebook_node, {"metadata": {"path": tmpdir}})

        nb_response = response_from_notebook(tmp_nb, manager)

        validator = json_validator(nb_response["starter"]["schema"])

        nb_response.update(body=body, name=name, path=path, status="continuing")

        try:
            validator(body)
            nb_response.update(status="done")
        except JsonSchemaException as err:
            manager.log.debug(f"🍪 validator: {err}")

        if nb_response["status"] == "done":
            roots = sorted(tdp.glob("*"))
            first_copied = None
            for root in roots:
                if root == tmp_nb:
                    continue
                first_copied = root
                await manager.start_copy(
                    "notebook-copy",
                    {
                        "label": "Copy Notebook Output",
                        "description": "just copies whatever notebook did",
                        "src": str(root),
                    },
                    path,
                    {},
                )
            nb_response.update(path=ujoin(path, first_copied.name))

        return nb_response
