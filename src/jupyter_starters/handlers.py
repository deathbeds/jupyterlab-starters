""" tornado handler for managing and communicating with language servers
"""
# pylint: disable=abstract-method
from typing import TYPE_CHECKING

from notebook.base.handlers import IPythonHandler
from notebook.utils import url_path_join as ujoin

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
        starters = self.manager.starters

        self.finish({"starters": starters})


class StarterHandler(BaseHandler):
    """ acts on a single starters
    """

    async def post(self, starter, path) -> None:
        """ start a starter
        """
        self.finish(await self.manager.start(starter, path))


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
