""" manager, for starters
"""
# pylint: disable=no-self-use,unsubscriptable-object,fixme
import base64
import importlib
from copy import deepcopy
from pathlib import Path
from typing import List, Text
from urllib.parse import unquote

import jinja2
import traitlets as T
from jupyter_core.paths import jupyter_config_path
from jupyter_server import _tz as tz
from jupyter_server.services.config import ConfigManager
from jupyter_server.utils import ensure_async, url_path_join as ujoin
from traitlets.config import LoggingConfigurable

from .py_starters.cookiecutter import cookiecutter_starters
from .py_starters.notebook import notebook_starter, response_from_notebook, stop_kernel
from .schema.v2 import STARTERS
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


class StarterManager(LoggingConfigurable):
    """handlers starting starters"""

    _starters = Schema(validator=STARTERS)
    jinja_env = T.Instance(jinja2.Environment)
    jinja_env_extensions = T.Dict()
    config_dict = T.Dict()
    kernel_dirs = T.Dict({})

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
        return jinja2.Environment(
            extensions=[
                ext for ext, enabled in self.jinja_env_extensions.items() if enabled
            ]
        )

    @T.default("config_dict")
    def _default_config_dict(self):
        """load merged config from more jupyter_*_config.d files

        re-uses notebook loading machinery to look through more locations
        """
        manager = ConfigManager(read_config_path=jupyter_config_path())
        conf = {}
        for app in ["_", "_notebook_", "_server_"]:
            conf.update(**manager.get(f"jupyter{app}config").get("StarterManager", {}))
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

        await self.save_one(root, dest)

        for child in iter_not_ignored(root, starter.get("ignore")):
            await self.save_one(
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

    async def save_one(self, src, dest):
        """use the contents manager to write a single file/folder"""
        # pylint: disable=broad-except

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

        allow_hidden = None

        if hasattr(self.contents_manager, "allow_hidden"):
            allow_hidden = self.contents_manager.allow_hidden
            self.contents_manager.allow_hidden = True

        try:
            await ensure_async(self.contents_manager.save(model, dest))
        except Exception as err:
            self.log.error(f"Couldn't save {dest}: {err}")
        finally:
            if allow_hidden is not None:
                self.contents_manager.allow_hidden = allow_hidden


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
