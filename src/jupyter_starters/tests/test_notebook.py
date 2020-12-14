""" tests of exotic notebook starter behavior
"""
import pytest

from jupyter_starters.types import Status


@pytest.mark.asyncio
async def test_notebook_no_schema(starter_manager, tmp_notebook):
    """does a notebook without a schema still work?
    https://github.com/deathbeds/jupyterlab-starters/issues/26
    """

    name = "tmp-notebook"
    starter_manager.extra_starters[name] = {
        "type": "notebook",
        "src": str(tmp_notebook),
        "description": "test",
        "label": "test",
    }

    response = await starter_manager.start(name, "", {})
    assert response["status"] == Status.DONE, response
