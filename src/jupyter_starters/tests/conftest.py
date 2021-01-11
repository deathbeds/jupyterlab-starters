""" common test stuff
"""
# pylint: disable=redefined-outer-name
import nbformat.v4
import pytest
import traitlets
from jupyter_client.multikernelmanager import MultiKernelManager
from jupyter_server.services.contents.filemanager import FileContentsManager
from jupyter_server.services.contents.manager import ContentsManager
from traitlets.config import LoggingConfigurable

from jupyter_starters.manager import StarterManager


class MockApp(LoggingConfigurable):
    """not really a nbapp"""

    kernel_manager = traitlets.Instance(MultiKernelManager)
    contents_manager = traitlets.Instance(ContentsManager)
    notebook_dir = traitlets.Unicode()

    @traitlets.default("kernel_manager")
    def _kernel_manager(self):
        """simplest reasonable kernel manager"""
        return MultiKernelManager(parent=self)

    @traitlets.default("contents_manager")
    def _contents_manager(self):
        """simplest reasonable kernel manager"""
        return FileContentsManager(root_dir=self.notebook_dir, parent=self)


@pytest.fixture
def starter_manager(mock_app):
    """an orphaned starter"""
    return StarterManager(parent=mock_app)


@pytest.fixture
def mock_app(monkeypatch, tmp_path):
    """a fake notebook app in a tmpdir"""
    monkeypatch.chdir(tmp_path)
    return MockApp(notebook_dir=str(tmp_path))


@pytest.fixture
def example_project(tmp_path):
    """a minimal project"""
    my_module = tmp_path / "my_module"
    starter_content = my_module / "starter_content"
    starter_content.mkdir(parents=True)

    (tmp_path / "README.md").write_text("# My Module\n")
    (my_module / "__init__.py").write_text("__version__ = '0.0.0\n")
    (starter_content / "example.txt").write_text("123")

    return tmp_path


@pytest.fixture
def tmp_notebook(tmp_path):
    """make an empty python notebook on disk"""
    notebook = nbformat.v4.new_notebook()
    notebook.metadata["kernelspec"] = {"name": "python3"}
    nb_path = tmp_path / "Untitled.ipynb"
    nb_path.write_text(nbformat.writes(notebook))
    return nb_path
