""" tests of content starter behavior
"""
from pathlib import Path

import pytest

from jupyter_starters.types import Status


@pytest.mark.asyncio
async def test_content(starter_manager, mock_app, caplog):
    """does a contents starter start?"""
    name = "tmp-content"
    starter_manager.extra_starters = {
        name: {
            "type": "content",
            "description": "test",
            "label": "test",
            "schema": {
                "type": "object",
                "properties": {"foo": {"type": "string"}, "bar": {"type": "string"}},
            },
            "content": {
                "type": "directory",
                "name": "{{ foo }} {{ foo }}",
                "content": [
                    {
                        "name": "{{ bar }}.txt",
                        "content": "{{ bar }}{{ bar }}",
                    },
                ],
            },
        }
    }

    response = await starter_manager.start(name, "", {"foo": "FOÖ", "bar": "BAR"})
    assert response["status"] == Status.DONE, response
    assert not caplog.record_tuples
    notebook_path = Path(mock_app.notebook_dir)
    barf = notebook_path / "FOÖ FOÖ/BAR.txt"
    assert barf.read_text() == "BARBAR"
