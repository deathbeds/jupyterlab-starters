""" manager, for starters
"""
# pylint: disable=no-self-use,unsubscriptable-object,fixme
import base64
import urllib.parse
from pathlib import Path
from typing import List, Text

import jinja2
import traitlets as T
from notebook import _tz as tz
from notebook.utils import url_path_join as ujoin
from traitlets.config import LoggingConfigurable

from .py_starters.cookiecutter import cookiecutter_starters
from .schema.v1 import STARTERS
from .trait_types import Schema

IGNORE_PATTERNS = [".ipynb_checkpoints", "node_modules", "envs"]


class StarterManager(LoggingConfigurable):
    """ handlers starting starters
    """

    starters = Schema(validator=STARTERS)
    extra_starters = Schema(default_value={}, validator=STARTERS).tag(config=True)
    jinja_env = T.Instance(jinja2.Environment)
    jinja_env_extensions = T.Dict()
    extra_jinja_env_extensions = T.Dict({}).tag(config=True)

    @property
    def contents_manager(self):
        """ use the contents manager from parent
        """
        return self.parent.contents_manager

    @T.default("jinja_env_extensions")
    def _default_env_extensions(self):
        extensions = {"jinja2_time.TimeExtension": True}
        extensions.update(self.extra_jinja_env_extensions)
        return extensions

    @T.default("jinja_env")
    def _default_env(self):
        return jinja2.Environment(
            extensions=[
                ext for ext, enabled in self.jinja_env_extensions.items() if enabled
            ]
        )

    @T.default("starters")
    def _default_starters(self):
        """ default starters
        """
        starters = {}
        starters.update(cookiecutter_starters())
        starters.update(self.extra_starters)
        return starters

    @property
    def starter_names(self) -> List[Text]:
        """ convenience method to get names of starters
        """
        return sorted(dict(self.starters).keys())

    async def start(self, name, path, body):
        """ start a starter
        """
        starter = self.starters[name]
        starter_type = starter["type"]

        if starter_type == "copy":
            return await self._start_copy(name, starter, path, body)

        if starter_type == "python":
            return await self._start_python(name, starter, path, body)

        raise NotImplementedError(starter["type"])

    async def _start_copy(self, name, starter, path, body):
        root = Path(starter["src"]).resolve()

        root_uri = root.as_uri()

        dest_tmpl_str = starter.get("dest")

        if dest_tmpl_str is not None:
            dest_tmpl = self.jinja_env.from_string(dest_tmpl_str)
            dest = ujoin(path, dest_tmpl.render(**(body or {})))
        else:
            dest = ujoin(path, root.name)

        await self.save_one(root, dest)

        if root.is_dir():
            for src in sorted(root.rglob("*")):
                src_uri = src.as_uri()
                if any([ignore in src_uri for ignore in IGNORE_PATTERNS]):
                    continue
                await self.save_one(
                    src,
                    urllib.parse.unquote(ujoin(dest, src_uri.replace(root_uri, ""))),
                )
        # TODO: add to schema, normalize
        return {"name": name, "starter": starter, "path": dest}

    async def _start_python(self, name, starter, path, body):
        func = T.import_item(starter["callable"])
        return await func(name, starter, path, body, self)

    async def save_one(self, src, dest):
        """ use the contents manager to write a single file/folder
        """
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

        self.contents_manager.save(model, dest)
