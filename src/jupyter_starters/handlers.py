""" tornado handler for managing and communicating with language servers
"""
# pylint: disable=abstract-method
from typing import TYPE_CHECKING

from notebook.base.handlers import IPythonHandler
from notebook.utils import url_path_join as ujoin

from ._json import JsonSchemaException, loads
from .schema.v1 import ALL_STARTERS
from .types import NS

if TYPE_CHECKING:
    from .manager import StarterManager


class BaseHandler(IPythonHandler):
    """ common base handlers
    """

    manager = None  # type: StarterManager

    def initialize(self, manager) -> None:
        """ capture the manager
        """
        self.manager = manager


class StartersHandler(BaseHandler):
    """ serves the available starters
    """

    async def get(self) -> None:
        """ return the starters
        """
        response = {"starters": self.manager.starters}

        try:
            ALL_STARTERS(response)
        except JsonSchemaException as err:
            self.manager.log.warn(f"[starter] invalid response: {err}")

        self.finish(response)


class StarterHandler(BaseHandler):
    """ acts on a single starters
    """

    async def post(self, starter, path) -> None:
        """ start a starter
        """
        body = None

        if self.request.body:
            body = loads(self.request.body)

        self.finish(await self.manager.start(starter, path, body))


def add_handlers(nbapp, manager) -> None:
    """ Add starter routes to the notebook server web application
    """

    opts = {"manager": manager}

    nbapp.web_app.add_handlers(
        ".*",
        [
            (ujoin(nbapp.base_url, NS), StartersHandler, opts),
            (
                ujoin(nbapp.base_url, NS, "(?P<starter>.*?)", "(?P<path>.*?)"),
                StarterHandler,
                opts,
            ),
        ],
    )
