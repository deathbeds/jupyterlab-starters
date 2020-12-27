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


GH = "https://github.com"
GITHUB_TOPIC = f"{GH}/topics/cookiecutter-template"
GITHUB_SEARCH = f"{GH}/search?utf8=%E2%9C%93&q=path%3A%2F+filename%3Acookiecutter.json"

JUPYTER_COOKIECUTTERS = [
    {
        "repo": f"{GH}/jupyter/cookiecutter-docker-stacks",
        "description": "Cookiecutter for community-maintained Jupyter Docker images",
    },
    {
        "repo": f"{GH}/jupyter-widgets/widget-ts-cookiecutter",
        "description": (
            "A highly opinionated cookiecutter template for" "ipywidget extensions."
        ),
    },
    {
        "repo": f"{GH}/jupyter-widgets/widget-cookiecutter",
        "description": (
            "A cookiecutter template for creating a custom Jupyter" "widget project."
        ),
    },
    {
        "repo": f"{GH}/jupyterlab/extension-cookiecutter-js",
        "description": "A cookiecutter recipe for building JupyterLab extensions.",
    },
    {
        "repo": f"{GH}/jupyterlab/extension-cookiecutter-ts",
        "description": "A cookiecutter recipe for JupyterLab extensions in Typescript",
    },
    {
        "repo": f"{GH}/jupyterlab/mimerender-cookiecutter-ts",
        "description": (
            "Cookie cutter for JupyterLab mimerenderer" "extensions using TypeScript"
        ),
    },
    {
        "repo": f"{GH}/jupyterlab/theme-cookiecutter",
        "description": (
            "A cookiecutter template to help you make" "new JupyterLab theme extensions"
        ),
    },
]


def cookiecutter_starters(manager):
    """try to find some cookiecutters"""
    try:
        cookiecutter = __import__("cookiecutter")
    except (ImportError, ValueError):
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
                    },
                },
            },
            "uiSchema": {
                "template": {"ui:autofocus": True},
                "checkout": {"ui:placeholder": "master"},
            },
        }
    }


def cookiecutter_pantry():
    """try to load the pantry from the cookiecutter metadata"""
    grouped = {"Jupyter": JUPYTER_COOKIECUTTERS}

    try:
        metadata = __import__("importlib_metadata").metadata

        ccmd = (
            str(metadata("cookiecutter")).split("Pantry")[1].split("\n## ")[0].strip()
        )

        groups = ccmd.split("### ")[1:]

        for group in groups:
            name = group.split("\n")[0].strip()
            grouped[name] = [
                dict(repo=m[1], description=m[2])
                for m in sorted(re.findall(r"\* \[(.*?)]\((.*?)\)[\s:]*(.*?)\n", group))
            ]

        specials = (
            str(metadata("cookiecutter"))
            .split("Cookiecutter Specials")[1]
            .split("\n## ")[0]
            .strip()
        )

        grouped["Cookiecutter Specials"] = [
            dict(repo=m[1], description=m[2])
            for m in sorted(re.findall(r"\* \[(.*?)]\((.*?)\)[\s:]*(.*?)\n", specials))
        ]

    except (ImportError, ValueError, AttributeError):
        pass

    grouped = dict(sorted(grouped.items()))

    return [
        {
            "title": name,
            "enum": [t["repo"] for t in templates],
            "enumNames": [
                f"""{"/".join(t["repo"].split("/")[-2:])}: {t["description"]}"""
                for t in templates
            ],
            "default": templates[0]["repo"],
        }
        for name, templates in grouped.items()
    ]


async def start(name, starter, path, body, manager) -> Dict[Text, Any]:
    """run cookiecutter"""
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


def cookiecutter_to_schema(cookiecutter):
    """convert a cookiecutter context to a JSON schema"""
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
