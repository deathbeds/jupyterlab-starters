""" serverextension for starters
"""
from .handlers import add_handlers
from .manager import StarterManager


def load_jupyter_server_extension(nbapp):
    """ create a StarterManager and add handlers
    """
    manager = StarterManager(contents_manager=nbapp.contents_manager)
    add_handlers(nbapp, manager)
