""" manager, for starters
"""
# pylint: disable=no-self-use,unsubscriptable-object
import base64

import traitlets as T
from notebook import _tz as tz
from notebook.utils import url_path_join as ujoin
from traitlets.config import LoggingConfigurable

from .schema.v1 import STARTERS
from .trait_types import Schema


class StarterManager(LoggingConfigurable):
    """ handlers starting starters
    """

    starters = Schema(validator=STARTERS).tag(config=True)

    @property
    def contents_manager(self):
        """ use the contents manager from parent
        """
        return self.parent.contents_manager

    @T.default("starters")
    def _default_starters(self):
        """ default starters
        """
        return {}

    async def start(self, starter, path):
        """ start a starter
        """
        root = self.starters[starter]["root"]
        root_uri = root.as_uri()
        dest = ujoin(path, starter)

        await self.save_one(root, dest)

        for src in sorted(root.rglob("*")):
            await self.save_one(src, ujoin(dest, src.as_uri().replace(root_uri, "")))

        return {"starter": starter, "path": dest}

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
