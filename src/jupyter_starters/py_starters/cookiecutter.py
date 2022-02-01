""" a starter that runs cookiecutter
"""
# pylint: disable=cyclic-import,duplicate-code,broad-except

import re
import shutil
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any, Dict, Text

from jupyter_server.utils import url_path_join as ujoin

from ..json_ import JsonSchemaException, json_validator
from ..types import Status

if TYPE_CHECKING:
    from ..manager import StarterManager  # noqa

try:
    import cookiecutter.main

    HAS_COOKIECUTTER = True
    HAS_DIRECTORY = cookiecutter.__version__ >= "1.7.1"
except ImportError:
    HAS_COOKIECUTTER = False
    HAS_DIRECTORY = False


GH = "https://github.com"
GITHUB_TOPIC = f"{GH}/topics/cookiecutter-template"
GITHUB_SEARCH = f"{GH}/search?utf8=%E2%9C%93&q=path%3A%2F+filename%3Acookiecutter.json"

JUPYTER_COOKIECUTTERS = {
    "Jupyter Docker Environments": [
        {
            "repo": f"{GH}/jupyter/cookiecutter-docker-stacks",
            "description": (
                "Cookiecutter for community-maintained Jupyter " "Docker images"
            ),
        },
    ],
    "Jupyter Widgets": [
        {
            "repo": f"{GH}/jupyter-widgets/widget-ts-cookiecutter",
            "description": (
                "A highly opinionated cookiecutter template for" "ipywidget extensions."
            ),
        },
        {
            "repo": f"{GH}/jupyter-widgets/widget-cookiecutter",
            "description": (
                "A cookiecutter template for creating a custom Jupyter"
                "widget project."
            ),
        },
    ],
    "JupyterLab Extensions": [
        {
            "repo": f"{GH}/jupyterlab/extension-cookiecutter-js",
            "description": "A cookiecutter recipe for building JupyterLab extensions.",
        },
        {
            "repo": f"{GH}/jupyterlab/extension-cookiecutter-ts",
            "description": (
                "A cookiecutter recipe for JupyterLab extensions in Typescript"
            ),
        },
        {
            "repo": f"{GH}/jupyterlab/mimerender-cookiecutter-ts",
            "description": (
                "Cookie cutter for JupyterLab mimerenderer"
                "extensions using TypeScript"
            ),
        },
    ],
    "JupyterLite Extensions": [
        {
            "repo": f"{GH}/jupyterlite/serverlite-cookiecutter-ts",
            "description": "A cookiecutter for a JupyterLite Kernel",
        },
    ],
    **(
        {}
        if not HAS_DIRECTORY
        else {
            "Jupyter Server Proxy": [
                {
                    "repo": f"{GH}/jupyterhub/jupyter-server-proxy",
                    "description": (
                        "Configure a jupyter-server-proxy "
                        "(use directory: `contrib/template`)"
                    ),
                }
            ],
        }
    ),
}


def cookiecutter_starters(manager):
    """try to find some cookiecutters"""
    if not HAS_COOKIECUTTER:
        manager.log.debug(
            "🍪 install cookiecutter to enable the cookiecutter starter. yum!"
        )
        return {}

    return {
        "cookiecutter": {
            "label": "Cookiecutter",
            "description": f"Cookiecutter {cookiecutter.__version__}",
            "type": "python",
            "callable": "jupyter_starters.py_starters.cookiecutter.start",
            "schema": {
                "type": "object",
                "required": ["template"],
                "properties": {
                    "template": {
                        "title": "Template",
                        "type": "string",
                        "description": (
                            "Directory or URL of template. "
                            f" Find more on GitHub by [topic]({GITHUB_TOPIC}) "
                            f" or [advanced search]({GITHUB_SEARCH})."
                        ),
                        "anyOf": [
                            {"type": "string", "title": "Enter URL"},
                            *cookiecutter_pantry(),
                        ],
                    },
                    "checkout": {
                        "title": "Checkout",
                        "description": "The branch, tag, or commit ID to use",
                        "type": "string",
                        "default": "HEAD",
                    },
                    **{
                        "directory": {
                            "title": "Directory",
                            "description": (
                                "Relative path to a cookiecutter "
                                "template in a repository."
                            ),
                            "type": "string",
                            "default": "",
                        }
                        if HAS_DIRECTORY
                        else {}
                    },
                },
            },
            "uiSchema": {"template": {"ui:autofocus": True}},
        }
    }


def cookiecutter_pantry():
    """try to load the pantry from the cookiecutter metadata"""
    grouped = {**JUPYTER_COOKIECUTTERS}

    return [
        {
            "title": name,
            "enum": [t["repo"] for t in templates],
            "enumNames": [
                f"""{"/".join(t["repo"].split("/")[-2:])}: {t["description"]}"""
                for t in templates
            ],
            "default": sorted(templates, key=lambda t: t["repo"])[0]["repo"],
        }
        for name, templates in grouped.items()
    ]


async def start(name, starter, path, body, manager) -> Dict[Text, Any]:
    """run cookiecutter"""
    # pylint: disable=cyclic-import,broad-except,too-many-locals,unused-variable
    template = body["template"]
    checkout = body.get("checkout")

    manager.log.debug(f"🍪 body: {body}")

    config_dict = cookiecutter.main.get_user_config()

    repo_dir_kwargs = dict(
        template=template,
        abbreviations=config_dict["abbreviations"],
        clone_to_dir=config_dict["cookiecutters_dir"],
        checkout=checkout,
        no_input=True,
        password=None,
    )

    if HAS_DIRECTORY:
        directory = body.get("directory")
        repo_dir_kwargs.update(directory=directory)

    repo_dir, cleanup = cookiecutter.main.determine_repo_dir(**repo_dir_kwargs)

    manager.log.debug(f"🍪 repo_dir: {repo_dir}")

    context_file = Path(repo_dir) / "cookiecutter.json"

    base_context = dict(
        cookiecutter.main.generate_context(
            context_file=str(context_file),
            default_context=config_dict["default_context"],
            extra_context={},
        )
    )

    manager.log.debug(f"🍪 base_context: {base_context}")

    schema, ui_schema = cookiecutter_to_schema(base_context["cookiecutter"])

    manager.log.debug(f"🍪 schema: {schema}")

    new_starter = deepcopy(starter)
    new_starter["schema"]["required"] += ["cookiecutter"]
    new_starter["schema"]["properties"]["cookiecutter"] = schema
    new_starter.setdefault("uiSchema", {})["cookiecutter"] = ui_schema

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
            "status": Status.CONTINUING,
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
                await manager.just_copy(root, path)

            if cleanup:
                shutil.rmtree(repo_dir)

            return {
                "body": body,
                "name": name,
                "path": ujoin(path, roots[0].name),
                "starter": new_starter,
                "status": Status.DONE,
            }
        except Exception as err:
            manager.log.exception("🍪 error")
            if cleanup:
                shutil.rmtree(repo_dir)
            return {
                "body": body,
                "name": name,
                "path": path,
                "starter": new_starter,
                "status": Status.CONTINUING,
                "errors": [str(err)],
            }


def cookiecutter_to_schema(cookiecutter_json):
    """convert a cookiecutter context to a JSON schema"""
    bools = {"y": True, "n": False}
    schema = {
        "title": "Cookiecutter",
        "description": "Values to use in template variables",
        "type": "object",
        "properties": {},
    }
    ui_schema = {}
    schema["properties"] = properties = {}

    for field, value in cookiecutter_json.items():
        title = field.replace("_", " ").replace("-", " ").title()
        if isinstance(value, str):
            if value in bools:
                properties[field] = {
                    "type": "string",
                    "default": value,
                    "title": title,
                    "enum": [*bools.keys()],
                    "enumNames": ["yes", "no"],
                }
                ui_schema[field] = {"ui:widget": "radio"}
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
    return schema, ui_schema
