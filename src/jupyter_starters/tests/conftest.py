""" common test stuff
"""
import pytest

from jupyter_starters.manager import StarterManager


@pytest.fixture
def starter_manager():
    """ an orphaned starter
    """
    return StarterManager()


@pytest.fixture
def example_project(tmp_path):
    """ a minimal project
    """
    my_module = tmp_path / "my_module"
    starter_content = my_module / "starter_content"
    starter_content.mkdir(parents=True)

    (tmp_path / "README.md").write_text("# My Module\n")
    (my_module / "__init__.py").write_text("__version__ = '0.0.0\n")
    (starter_content / "example.txt").write_text("123")

    return tmp_path
