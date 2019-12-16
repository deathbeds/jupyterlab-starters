""" a starter that runs cookiecutter
"""
# pylint: disable=cyclic-import

import re
import shutil
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any, Dict, Text

from notebook.utils import url_path_join as ujoin

from .._json import JsonSchemaException, json_validator

if TYPE_CHECKING:
    from ..manager import StarterManager  # noqa

DEFAULT_TEMPLATE = "https://github.com/audreyr/cookiecutter-pypackage.git"


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
                    },
                },
            },
        }
    }


async def start(name, starter, path, body, manager) -> Dict[Text, Any]:
    """ run cookiecutter
    """
    # pylint: disable=cyclic-import,broad-except,too-many-locals,unused-variable
    template = body["template"]
    checkout = body.get("checkout") or None
    manager.log.debug(f"🍪 body: {body}")

    cookiecutter = __import__("cookiecutter.main")

    config_dict = cookiecutter.main.get_user_config()

    repo_dir, cleanup = cookiecutter.main.determine_repo_dir(
        template=template,
        abbreviations=config_dict["abbreviations"],
        clone_to_dir=config_dict["cookiecutters_dir"],
        checkout=checkout,
        no_input=True,
        password=None,
    )

    manager.log.debug(f"🍪 repo_dir: {repo_dir}")

    context_file = Path(repo_dir) / "cookiecutter.json"

    base_context = cookiecutter.main.generate_context(
        context_file=str(context_file),
        default_context=config_dict["default_context"],
        extra_context={},
    )

    manager.log.debug(f"🍪 base_context: {base_context}")

    schema = cookiecutter_to_schema(base_context["cookiecutter"])

    manager.log.debug(f"🍪 schema: {schema}")

    new_starter = deepcopy(starter)
    new_starter["schema"]["required"] += ["cookiecutter"]
    new_starter["schema"]["properties"]["cookiecutter"] = schema

    validator = json_validator(new_starter["schema"])

    valid = False

    try:
        validator(body)
        valid = True
    except JsonSchemaException as err:
        manager.log.debug(f"🍪 validator: {err}")

    if not valid:
        return {
            "body": body,
            "name": name,
            "path": path,
            "starter": new_starter,
            "status": "continuing",
        }

    with TemporaryDirectory() as tmpd:
        final_context = {"cookiecutter": body["cookiecutter"]}
        final_context["cookiecutter"]["_template"] = template
        try:
            result = cookiecutter.main.generate_files(
                repo_dir=repo_dir,
                context=final_context,
                overwrite_if_exists=True,
                output_dir=tmpd,
            )
            manager.log.debug(f"result {result}")

            roots = sorted(Path(tmpd).glob("*"))
            for root in roots:
                await manager.start_copy(
                    "cookiecutter-copy",
                    {
                        "label": "Copy Cookiecutter",
                        "description": "just copies whatever cookiecutter did",
                        "src": str(root),
                    },
                    path,
                    {},
                )

            if cleanup:
                shutil.rmtree(repo_dir)

            return {
                "body": body,
                "name": name,
                "path": ujoin(path, roots[0].name),
                "starter": new_starter,
                "status": "done",
            }
        except Exception as err:
            manager.log.exception(f"🍪 error")
            if cleanup:
                shutil.rmtree(repo_dir)
            return {
                "body": body,
                "name": name,
                "path": path,
                "starter": new_starter,
                "status": "continuing",
                "errors": [str(err)],
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
        title = field.replace("_", " ").replace("-", " ").title()
        if isinstance(value, str):
            if value in bools:
                properties[field] = {
                    "type": "boolean",
                    "default": bools[value],
                    "title": title,
                }
                continue

            value_no_tmpl = re.sub(r"{[%{].*?[%}]}", "", value)

            properties[field] = {
                "type": "string",
                "description": f"default: {value}",
                "default": value_no_tmpl,
                "title": title,
                "minLength": 1,
            }
            continue

        if isinstance(value, dict):
            enum = list(value.keys())
            properties[field] = {"enum": enum, "default": enum[0], "title": title}
            continue

        if isinstance(value, list):
            properties[field] = {"enum": value, "default": value[0], "title": title}
            continue

    schema["required"] = sorted(list(schema["properties"].keys()))
    return schema
