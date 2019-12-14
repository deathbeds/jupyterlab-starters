""" tornado handler for managing and communicating with language servers
"""
from notebook.base.handlers import IPythonHandler
from notebook.utils import url_path_join as ujoin

from .types import NS


class BaseHandler(IPythonHandler):
    manager = None

    def initialize(self, manager):
        self.manager = manager


class StartersHandler(BaseHandler):
    async def get(self):
        starters = await self.manager.starters()

        self.finish({"starters": starters})


class StarterHandler(BaseHandler):
    async def post(self, starter, path):
        self.finish(await self.manager.start(starter, path))


def add_handlers(nbapp, manager):
    """ Add starter routes to the notebook server web application
    """

    opts = {"manager": manager}

    nbapp.web_app.add_handlers(
        ".*",
        [
            (ujoin(nbapp.base_url, NS), StartersHandler, opts),
            (ujoin(nbapp.base_url, NS, "(?P<starter>.*?)", "(?P<path>.*?)"), StarterHandler, opts),
        ],
    )
