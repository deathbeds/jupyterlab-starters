""" tornado handler for managing and communicating with language servers
"""
# pylint: disable=abstract-method
from typing import TYPE_CHECKING

from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.utils import url_path_join as ujoin

from .json_ import JsonSchemaException, loads
from .schema.v2 import ALL_STARTERS, VERSION
from .types import NS

if TYPE_CHECKING:
    from .manager import StarterManager


class BaseHandler(JupyterHandler):
    """common base handlers"""

    manager = None  # type: StarterManager

    def initialize(self, manager) -> None:
        """capture the manager"""
        self.manager = manager


class StartersHandler(BaseHandler):
    """serves the available starters"""

    async def get(self) -> None:
        """return the starters"""
        response = {
            "version": VERSION,
            "starters": self.manager.starters,
            "running": self.manager.running,
        }

        try:
            ALL_STARTERS(response)
        except JsonSchemaException as err:
            self.manager.log.warn(f"[starter] invalid response: {err}")

        self.finish(response)


class StarterHandler(BaseHandler):
    """acts on a single starters"""

    async def post(self, starter, path) -> None:
        """start a starter"""
        body = None

        if self.request.body:
            body = loads(self.request.body)

        self.finish(await self.manager.start(starter, path, body))

    # pylint: disable=unused-argument

    async def delete(self, starter, path=None) -> None:
        """forcibly stop a starter"""
        await self.manager.stop(starter)
        self.set_status(202)
        self.finish({})


def add_handlers(nbapp, manager) -> None:
    """Add starter routes to the notebook server web application"""

    opts = {"manager": manager}

    url = ujoin(nbapp.base_url, NS)
    starter_url = ujoin(url, "(?P<starter>.*?)", "(?P<path>.*?)", "?$")
    nbapp.log.debug("💡 starters will list under %s", url)
    nbapp.log.debug("💡 starters will run under %s", starter_url)

    nbapp.web_app.add_handlers(
        ".*",
        [
            (url, StartersHandler, opts),
            (
                starter_url,
                StarterHandler,
                opts,
            ),
        ],
    )
