"""Tests of content starter behavior."""
# pylint: disable=redefined-outer-name
from pathlib import Path

import pytest

from jupyter_starters.types import Status

from .. import json_

BAR = "BÄR"
FOO = "FOÖ"


def _is_bar_notebook(nb_path: Path):
    """does the generated notebook roughly match expectation?"""
    nb_bytes = nb_path.read_bytes()
    ipynb = json_.loads(nb_bytes.decode("utf-8"))
    code, markdown, raw = ipynb["cells"]

    assert ipynb["metadata"]["foo"] == BAR

    assert code["source"] == [f"print('{BAR}')"]
    assert code["metadata"]["foo"] == BAR
    assert code["cell_type"] == "code"

    assert markdown["source"] == [f"# {BAR}"]
    assert markdown["cell_type"] == "markdown"

    assert raw["source"] == [BAR]
    assert raw["cell_type"] == "raw"

    return True


CONTENT = {
    "text": [
        {"name": "{{ bar }}.txt", "content": "{{ bar }}{{ bar }}"},
        f"{BAR}.txt",
        lambda observed: observed.read_bytes() == f"{BAR}{BAR}".encode("utf-8"),
    ],
    "notebook": [
        {
            "name": "{{ bar }}.ipynb",
            "type": "notebook",
            "content": {
                "metadata": {"foo": "{{ bar }}"},
                "cells": [
                    {
                        "source": ["print('{{ bar }}')"],
                        "metadata": {"foo": "{{ bar }}"},
                    },
                    {"cell_type": "markdown", "source": ["# {{ bar }}"]},
                    {"cell_type": "raw", "source": ["{{ bar }}"]},
                ],
            },
        },
        f"{BAR}.ipynb",
        _is_bar_notebook,
    ],
}


@pytest.mark.asyncio
async def test_content_file(a_content_starter, a_content_file, starter_manager, caplog):
    """does a contents starter file start?"""
    name = "tmp-content-file"
    template, path, content_is = a_content_file

    starter_manager.extra_starters = {
        name: {
            **a_content_starter,
            "content": template,
        }
    }

    response = await starter_manager.start(name, "", {"foo": FOO, "bar": BAR})
    assert response["status"] == Status.DONE, response
    barf = Path(starter_manager.parent.notebook_dir) / path
    assert content_is(barf)
    assert not caplog.record_tuples


@pytest.mark.asyncio
async def test_content_folder(
    a_content_starter, a_content_file, starter_manager, caplog
):
    """does a contents starter with a folder start?"""
    name = "tmp-content-folder"
    child_template, child_path, child_content_is = a_content_file

    starter_manager.extra_starters = {
        name: {
            **a_content_starter,
            "content": {
                "type": "directory",
                "name": "{{ foo }} {{ foo }}",
                "content": [child_template],
            },
        }
    }

    response = await starter_manager.start(name, "", {"foo": FOO, "bar": BAR})
    assert response["status"] == Status.DONE, response
    barf = Path(starter_manager.parent.notebook_dir) / f"{FOO} {FOO}" / child_path
    assert child_content_is(barf)
    assert not caplog.record_tuples


@pytest.mark.asyncio
async def test_content_folder_empty(
    a_content_starter, a_content_file, starter_manager, caplog
):
    """does a contents starter with an empty folder do nothing?"""
    name = "tmp-content-folder"
    child_template, _child_path, _child_content_is = a_content_file

    starter_manager.extra_starters = {
        name: {
            **a_content_starter,
            "content": {
                "type": "directory",
                "name": "{{ foo }} {{ foo }}",
                "content": [
                    {
                        "type": "directory",
                        "name": "{{ not_a_variable }}",
                        "content": [child_template],
                    },
                ],
            },
        }
    }

    response = await starter_manager.start(name, "", {"foo": FOO, "bar": BAR})
    assert response["status"] == Status.DONE, response
    parent = Path(starter_manager.parent.notebook_dir) / f"{FOO} {FOO}"
    assert parent.exists()
    children = sorted(parent.rglob("*"))
    assert not children, "unexpected child content"
    assert not caplog.record_tuples


@pytest.fixture
def a_content_starter():
    """A fragmaent of a content starter without content."""
    return {
        "type": "content",
        "description": "test",
        "label": "test",
        "schema": {
            "type": "object",
            "properties": {"foo": {"type": "string"}, "bar": {"type": "string"}},
        },
    }


@pytest.fixture(params=[*CONTENT.keys()])
def a_content_file(request):
    """an example of expected child content."""
    return CONTENT[request.param]
