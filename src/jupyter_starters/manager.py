from pathlib import Path
import base64

import traitlets as T
from traitlets.config import LoggingConfigurable
from notebook.services.contents.manager import ContentsManager
from notebook.utils import url_path_join as ujoin
from notebook import _tz as tz


class StarterManager(LoggingConfigurable):
    contents_manager = T.Instance(ContentsManager)

    starters = T.Dict()

    @T.default("starters")
    def starters(self):
        return {}

    async def start(self, starter, path):
        root = self.starters[starter]["root"]
        root_uri = root.as_uri()
        dest = ujoin(path, starter)

        await self.save_one(root, dest)

        for src in sorted(root.rglob("*")):
            await self.save_one(src, ujoin(dest, src.as_uri().replace(root_uri, "")))

        return {
            "starter": starter,
            "path": dest
        }

    async def save_one(self, src, dest):
        stat = src.stat()
        is_dir = src.is_dir()

        model = dict(
            name=src.name,
            type="directory" if is_dir else "file",
            path=dest,
            last_modified=tz.utcfromtimestamp(stat.st_mtime),
            created=tz.utcfromtimestamp(stat.st_ctime),
            content=None if is_dir else base64.b64encode(src.read_bytes()).decode("utf-8"),
            format=None if is_dir else "base64",
            mimetype=None,
            size=stat.st_size
        )

        self.contents_manager.save(model, dest)
