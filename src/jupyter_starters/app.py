"""CLI for jupyter-starters"""
# pylint: disable=too-many-ancestors
import textwrap

import traitlets as T
from jupyter_core.application import JupyterApp, base_aliases, base_flags

from ._version import __version__
from .json_ import dumps
from .manager import StarterManager


class StartersBaseApp(JupyterApp):
    """A base class for CLI apps."""

    version = __version__

    @property
    def description(self):  # pragma: no cover
        """A human readable description."""
        return self.__doc__.splitlines()[0].strip()


class StartersListApp(StartersBaseApp):
    """List all installed starters."""

    json = T.Bool(False, help="output JSON").tag(config=True)

    manager = T.Instance(StarterManager)

    flags = dict(
        **base_flags,
        **{
            "json": (
                {"StartersListApp": {"json": True}},
                "List starters as JSON instead of YAML",
            ),
        },
    )

    aliases = dict(**base_aliases)

    def start(self):
        """List the installed starters."""
        starters = self.manager.starters
        if self.json:
            print(dumps(starters, indent=2, sort_keys=True))
        else:
            for name, starter in sorted(starters.items()):
                description = starter.get("description")
                label = starter.get("label", "(no label)")
                print(f"""{name}:""")
                print("  type:", starter.get("type", "(unknown)"))
                if label:
                    print(f"  label: {label}")
                if description:
                    print("  description: |-")
                print(textwrap.indent("\n".join(textwrap.wrap(description)), "    "))

    @T.default("manager")
    def _default_manager(self):
        return StarterManager(parent=self)


class StartersApp(StartersBaseApp):
    """jupyter-starters utilities"""

    name = "starters"
    subcommands = dict(
        list=(StartersListApp, f"{StartersListApp.__doc__}".splitlines()[0]),
    )


main = launch_instance = StartersApp.launch_instance

if __name__ == "__main__":  # pragma: no cover
    main()
