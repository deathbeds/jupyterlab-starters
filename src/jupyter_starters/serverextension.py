""" serverextension for starters
"""
from .handlers import add_handlers
from .manager import StarterManager


def load_jupyter_server_extension(nbapp):
    """create a StarterManager and add handlers"""
    manager = StarterManager(parent=nbapp)
    add_handlers(nbapp, manager)
    nbapp.log.info(f"""💡 starters: {", ".join(manager.starter_names)}""")
