""" a starter that runs cookiecutter
"""
from typing import Any, Dict, Text


COOKIECUTTER_STARTER = {
    "type": "python",
    "callable": "jupyter_starters.py_starters.cookiecutter:start",
    "schema": {
        "required": ["repo"],
        "properties": {
            "repo": {
                "title": "Cookiecutter Repository",
                "description": "URL of a cookiecutter",
                "type": "string",
                "pattern": "uri",
            },
            "branch": {
                "title": "Branch",
                "description": "branch of cookiecutter to use",
                "type": "string",
                "default": "master",
            },
        },
    },
}


async def start(path, body) -> Dict[Text, Any]:
    """ run cookiecutter
    """
    return {"path": path, "body": body}
