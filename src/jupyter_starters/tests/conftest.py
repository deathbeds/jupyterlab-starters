""" common test stuff
"""
import pytest

from jupyter_starters.manager import StarterManager


@pytest.fixture
def starter_manager():
    """ an orphaned starter
    """
    return StarterManager()
