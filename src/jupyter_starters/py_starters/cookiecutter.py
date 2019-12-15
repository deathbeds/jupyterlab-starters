""" a starter that runs cookiecutter
"""
# pylint: disable=cyclic-import

from copy import deepcopy
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Text

DEFAULT_TEMPLATE = "https://github.com/audreyr/cookiecutter-pypackage.git"

if TYPE_CHECKING:
    from ..manager import StarterManager  # noqa


def cookiecutter_starters():
    """ try to find some cookiecutters
    """
    try:
        cookiecutter = __import__("cookiecutter")
    except (ImportError, ValueError) as err:
        print(f"couldn't import cookiecutter: {err}")
        return {}

    return {
        "cookiecutter": {
            "label": "Cookiecutter",
            "description": f"Cookiecutter {cookiecutter.__version__}",
            "type": "python",
            "callable": "jupyter_starters.py_starters.cookiecutter.start",
            "schema": {
                "required": ["template"],
                "properties": {
                    "template": {
                        "title": "Template",
                        "description": "Directory or URL of template",
                        "type": "string",
                        "default": DEFAULT_TEMPLATE,
                    },
                    "checkout": {
                        "title": "Checkout",
                        "description": "The branch, tag or commit ID to use",
                        "type": "string",
                        "default": "master",
                    },
                },
            },
        }
    }


async def start(name, starter, path, body, manager) -> Dict[Text, Any]:
    """ run cookiecutter
    """
    template = body["template"]
    checkout = body["checkout"] or None

    cookiecutter = __import__("cookiecutter.main")

    manager.log.warn(f"{name} starting checkout")

    config_dict = cookiecutter.main.get_user_config()

    manager.log.warn(f"config_dict {config_dict}")

    repo_dir, cleanup = cookiecutter.main.determine_repo_dir(
        template=template,
        abbreviations=config_dict["abbreviations"],
        clone_to_dir=config_dict["cookiecutters_dir"],
        checkout=checkout,
        no_input=True,
        password=None,
    )

    manager.log.warn(f"repo_dir {repo_dir} cleanup {cleanup}")

    context_file = Path(repo_dir) / "cookiecutter.json"

    context = cookiecutter.main.generate_context(
        context_file=str(context_file),
        default_context=config_dict["default_context"],
        extra_context={},
    )

    manager.log.warn(f"context {context}")

    # prompt the user to manually configure at the command line.
    # except when 'no-input' flag is set
    # context['cookiecutter'] = prompt_for_config(context, no_input)

    # include template dir or url in the context dict
    # context["cookiecutter"]["_template"] = template

    schema = cookiecutter_to_schema(context["cookiecutter"])

    new_starter = deepcopy(starter)
    new_starter["schema"]["required"] += ["cookiecutter"]
    new_starter["schema"]["properties"]["cookiecutter"] = schema

    return {
        "body": body,
        "name": name,
        "path": path,
        "starter": new_starter,
        "status": "continuing",
    }


def cookiecutter_to_schema(cookiecutter):
    """ convert a cookiecutter context to a JSON schema
    """
    bools = {"y": True, "n": False}
    schema = {
        "title": "Cookiecutter",
        "description": "Values to use in template variables",
        "type": "object",
        "properties": {},
    }
    schema["properties"] = properties = {}

    for field, value in cookiecutter.items():
        if isinstance(value, str):
            if value in bools:
                properties[field] = {"type": "boolean", "default": bools[value]}
                continue

            properties[field] = {"type": "string", "default": value}
            continue

        if isinstance(value, dict):
            properties[field] = {"enum": list(value.keys())}
            continue

        if isinstance(value, list):
            properties[field] = {"enum": value}
            continue

        print(field, value)

    schema["required"] = sorted(list(schema["properties"].keys()))
    return schema
