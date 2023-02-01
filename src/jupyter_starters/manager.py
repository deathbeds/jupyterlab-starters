""" manager, for starters
"""
# pylint: disable=unsubscriptable-object,fixme
import base64
import importlib
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Text
from urllib.parse import unquote

import jinja2
import jinja2.sandbox
import nbformat
import traitlets as T
from jupyter_core.paths import jupyter_config_path
from jupyter_server import _tz as tz
from jupyter_server.services.config import ConfigManager
from jupyter_server.utils import ensure_async
from jupyter_server.utils import url_path_join as ujoin
from traitlets.config import LoggingConfigurable

from . import json_
from .py_starters.cookiecutter import cookiecutter_starters
from .py_starters.notebook import notebook_starter, response_from_notebook, stop_kernel
from .schema.v3 import STARTERS
from .trait_types import Schema
from .types import Status

# default patterns to ignore when copying
DEFAULT_IGNORE_PATTERNS = [
    "__pycache__",
    ".*_cache",
    ".git",
    ".ipynb_checkpoints",
    ".vscode",
    "*.egg-info",
    "*.pyc",
    "build",
    "dist",
    "node_modules",
    "Untitled.*",
]

#: the importable name of a class
DEFAULT_ENV_CLS = "jinja2.sandbox.SandboxedEnvironment"


def iter_not_ignored(root, ignore_patterns=None):
    """yield all children under a root that do not match the ignore patterns"""
    if not ignore_patterns:
        ignore_patterns = DEFAULT_IGNORE_PATTERNS

    if root.is_dir():
        ignored = set()
        for src in sorted(root.rglob("*")):
            if ignored & set(src.parents):
                continue

            root_rel = src.relative_to(root)

            if any(root_rel.match(pattern) for pattern in ignore_patterns):
                ignored.add(src)
                continue

            yield src


class StarterManager(LoggingConfigurable):
    """handlers starting starters"""

    _starters = Schema(validator=STARTERS)
    jinja_env = T.Instance(jinja2.Environment)
    jinja_env_extensions = T.Dict()
    config_dict = T.Dict()
    kernel_dirs = T.Dict({})

    jinja_env_cls = T.Unicode(DEFAULT_ENV_CLS).tag(config=True)
    extra_starters = Schema(default_value={}, validator=STARTERS).tag(config=True)
    extra_jinja_env_extensions = T.Dict({}).tag(config=True)

    @property
    def contents_manager(self):
        """use the contents manager from parent"""
        return self.parent.contents_manager

    @property
    def kernel_manager(self):
        """use the kernel manager from parent"""
        return self.parent.kernel_manager

    @property
    def running(self):
        """report names of all starters that could be stopped"""
        return list(self.kernel_dirs.keys())

    @T.default("jinja_env_extensions")
    def _default_env_extensions(self):
        """get env extensions from extras and config"""
        extensions = {}
        extensions.update(self.config_dict.get("extra_jinja_env_extensions", {}))
        extensions.update(self.extra_jinja_env_extensions)
        return extensions

    @T.default("jinja_env")
    def _default_env(self):
        # pylint: disable=broad-except
        try:
            env_class = T.import_item(self.jinja_env_cls)
        except Exception as err:
            self.log.warning(
                f"Using {DEFAULT_ENV_CLS}, couldn't import {self.jinja_env_cls}: {err}"
            )
            env_class = T.import_item(DEFAULT_ENV_CLS)

        return env_class(
            extensions=[
                ext for ext, enabled in self.jinja_env_extensions.items() if enabled
            ]
        )

    @T.default("config_dict")
    def _default_config_dict(self):
        """load merged config from more jupyter_*_config.d files

        re-uses notebook loading machinery to look through more locations
        """
        config_path = jupyter_config_path()
        cwd = str(Path.cwd())
        if cwd not in config_path:
            config_path = [cwd, *config_path]
        manager = ConfigManager(read_config_path=config_path)
        conf = {}
        for app in ["_", "_notebook_", "_server_"]:
            more_conf = manager.get(f"jupyter{app}config").get("StarterManager", {})
            conf.update(**more_conf)
        return conf

    @T.default("_starters")
    def _default_starters(self):
        """default starters"""
        starters = {}
        starters.update(cookiecutter_starters(self))
        starters.update(self.config_dict.get("extra_starters", {}))
        starters.update(self.extra_starters)
        return starters

    @property
    def starters(self):
        """augment notebook starters

        TODO: caching
        """
        starters = {}
        for name, starter in dict(self._starters).items():
            starter_copy = deepcopy(starter)

            if starter_copy["type"] == "notebook":
                src = self.resolve_src(starter)
                if src is None:
                    self.log.error(f"couldn't resolve starter {name}")
                    continue
                response = response_from_notebook(src)
                starter_copy.update(response.get("starter", {}))

            starters[name] = starter_copy

        return starters

    @property
    def starter_names(self) -> List[Text]:
        """convenience method to get names of starters"""
        return sorted(dict(self.starters).keys())

    async def start(self, name, path, body):
        """start a starter"""
        starter = self.starters[name]
        starter_type = starter["type"]

        if starter_type == "copy":
            return await self.start_copy(name, starter, path, body)

        if starter_type == "python":
            return await self.start_python(name, starter, path, body)

        if starter_type == "notebook":
            return await self.start_notebook(name, starter, path, body)

        if starter_type == "content":
            return await self.start_content(name, starter, path, body)

        raise NotImplementedError(starter["type"])

    async def stop(self, name):
        """stop a starter. presently only works for notebooks"""
        starter = self.starters[name]
        starter_type = starter["type"]

        if starter_type == "notebook":
            return await self.stop_notebook(name)

        raise NotImplementedError(starter["type"])

    def resolve_src(self, starter):
        """resolve the src of a file-based starter"""
        root = Path.cwd()
        if "src" not in starter:
            self.log.error("src is required")
            return None

        src = Path(starter["src"])

        if not src.is_absolute():
            py_src = starter.get("py_src")

            if py_src:
                spec = importlib.util.find_spec(py_src)
                if not spec:
                    self.log.error(f"Failed to import `py_src` {py_src}")
                    return None
                root = Path(spec.origin).parent

            src = (root / starter["src"]).resolve()

        if not src.exists():
            self.log.error(f"{src} does not exist")
            return None

        return src

    async def just_copy(self, root, path):
        """just copy, with some dummy values"""
        await self.start_copy(
            "just-copy",
            {
                "label": "Copy Something",
                "description": "just copies whatever",
                "src": str(root),
            },
            path,
            {},
        )

    async def start_copy(self, name, starter, path, body):
        """start a copy starter"""
        root = self.resolve_src(starter)

        if root is None:
            return None

        root_uri = root.as_uri()

        dest_tmpl_str = starter.get("dest")

        if dest_tmpl_str is not None:
            dest_tmpl = self.jinja_env.from_string(dest_tmpl_str)
            dest = ujoin(path, dest_tmpl.render(**(body or {})))
        else:
            dest = ujoin(path, root.name)

        await self.save_one_file(root, dest)

        for child in iter_not_ignored(root, starter.get("ignore")):
            await self.save_one_file(
                child,
                unquote(ujoin(dest, child.as_uri().replace(root_uri, ""))),
            )

        return {
            "body": body,
            "name": name,
            "path": dest,
            "starter": starter,
            "status": Status.DONE,
        }

    async def start_content(self, name, starter, path, body):
        """start a content starter"""

        dest = await self.save_content(path, starter["content"], body)

        return {
            "body": body,
            "name": name,
            "path": dest,
            "starter": starter,
            "status": Status.DONE,
        }

    async def start_python(self, name, starter, path, body):
        """start a python starter"""
        func = T.import_item(starter["callable"])
        return await func(name, starter, path, body, self)

    async def start_notebook(self, name, starter, path, body):
        """delegate running the notebook to a kernel"""
        return await notebook_starter(name, starter, path, body, self)

    async def stop_notebook(self, name):
        """stop running the notebook kernel"""
        return await stop_kernel(name, self)

    async def save_one_file(self, src, dest):
        """generate and save a content model for a single file/directory"""
        stat = src.stat()
        is_dir = src.is_dir()

        model = dict(
            name=src.name,
            type="directory" if is_dir else "file",
            path=dest,
            last_modified=tz.utcfromtimestamp(stat.st_mtime),
            created=tz.utcfromtimestamp(stat.st_ctime),
            content=None
            if is_dir
            else base64.b64encode(src.read_bytes()).decode("utf-8"),
            format=None if is_dir else "base64",
            mimetype=None,
            size=stat.st_size,
        )

        await self.save_contents_model(model, dest)

    def _template_notebook(self, content, body):
        """build a template notebook by manipulation"""
        json_text = json_.dumps(content, indent=2, sort_keys=True)
        content_tmpl = self.jinja_env.from_string(json_text)
        content_notebook = json_.loads(content_tmpl.render(**body))
        ipynb = nbformat.v4.new_notebook(metadata=content_notebook.get("metadata", {}))
        cells = []
        for a_cell in content_notebook.get("cells", []):
            cell_type = a_cell.get("cell_type", "code")
            source = a_cell.pop("source", "")
            if cell_type == "code":
                cell = nbformat.v4.new_code_cell(source, **a_cell)
            elif cell_type == "markdown":
                cell = nbformat.v4.new_markdown_cell(source, **a_cell)
            elif cell_type == "raw":
                cell = nbformat.v4.new_raw_cell(source, **a_cell)
            cells += [cell]
        ipynb["cells"] = cells

        nb_json = nbformat.v4.nbjson.writes(ipynb)
        return json_.loads(nb_json)

    async def save_content(self, path, starter_model, body):
        """save a content model (and its children)"""
        body = body or {}
        name_tmpl = self.jinja_env.from_string(starter_model["name"])
        name = name_tmpl.render(**body).strip()

        if not name:
            return

        dest = ujoin(path, name)

        type_ = starter_model.get("type", "file")

        is_dir = type_ == "directory"

        model = dict(
            name=name,
            path=dest,
            type=type_,
            last_modified=datetime.now(timezone.utc),
            created=datetime.now(timezone.utc),
        )

        if is_dir:
            model.update(
                content=None,
                size=0,
                format=None,
                mimetype=None,
            )
        elif type_ == "notebook":
            content = self._template_notebook(starter_model["content"], body)
            model.update(
                content=content,
                size=0,
                format="json",
                mimetype="application/x-ipynb+json",
            )
        else:
            content_tmpl = self.jinja_env.from_string(starter_model["content"])
            content = content_tmpl.render(**body)
            model.update(
                content=content,
                size=len(content),
                format=starter_model.get("format") or "text",
                mimetype=starter_model.get("mimetype") or "text/plain",
            )

        await self.save_contents_model(model, dest)

        if is_dir:
            for child in starter_model.get("content", []):
                await self.save_content(dest, child, body)

    async def save_contents_model(self, model, dest):
        """use the contents manager to write a model"""
        # pylint: disable=broad-except

        allow_hidden = None

        if hasattr(self.contents_manager, "allow_hidden"):
            allow_hidden = self.contents_manager.allow_hidden
            self.contents_manager.allow_hidden = True

        try:
            await ensure_async(self.contents_manager.save(model, dest))
        finally:
            if allow_hidden is not None:
                self.contents_manager.allow_hidden = allow_hidden
