# jupyterlab-starters

> _Parameterized file and directory starters for JupyterLab._

|                                  releases                                   |                  deps                   |         ci          |            demo             |                                          docs                                           |
| :-------------------------------------------------------------------------: | :-------------------------------------: | :-----------------: | :-------------------------: | :-------------------------------------------------------------------------------------: |
| [![pypi-badge][]][pypi] [![npm-badge][]][npm] [![license-badge][]][license] | ![python-badge][] ![jupyterlab-badge][] | [![ci-badge][]][ci] | [![binder-badge][]][binder] | [![docs-badge][]][docs] [![roadmap-badge][]][roadmap] [![changelog-badge][]][changelog] |

![screenshot][]

## What's a starter?

A starter is a...

- single file
- directory
- python function
- [cookiecutter][]
- notebook

... that creates a...

- single file
- directory of files (or more directories)

... that shows up **where you want it** in JupyterLab **at the click of a button**

## Installing

> You'll need `jupyterlab >=3,<4`, `python >=3.6`, and `nodejs >=12`

```bash
pip install --pre jupyter_starters
```

Check your installation:

```bash
jupyter serverextension list
jupyter labextension list
```

If you don't see `jupyterlab_starters` run:

```bash
jupyter serverextension enable --sys-prefix jupyterlab_starters
```

## Configuring

Like the Jupyter Notebook server, JupyterHub and other Jupyter interactive computing
tools, `jupyter-starters` can be configured via [Python or JSON files][notebook-config]
in _well-known locations_. You can find out where to put them on your system with:

```bash
jupyter --paths
```

They will be merged from bottom to top, and the directory where you launch your
`notebook` server wins, making it easy to check in to version control.

The very simplest starter, `copy`, will copy a file or folder to the location
it is launched from in the JupyterLab [Launcher][].

```json
{
  "StarterManager": {
    "extra_starters": {
      "whitepaper-single": {
        "type": "copy",
        "label": "Whitepaper Notebook",
        "description": "A reusable notebook for proposing research",
        "src": "examples/whitepaper-single.ipynb"
      }
    }
  }
}
```

> more docs TBD: for now, see examples in the [demo configuration][conf].

## Alternatives

Don't like what you see here? Try these other approaches:

- [jupyterlab_templates](https://github.com/timkpaine/jupyterlab_templates)

[binder-badge]: https://mybinder.org/badge_logo.svg
[binder]: https://mybinder.org/v2/gh/deathbeds/jupyterlab-starters/master?urlpath=lab
[changelog-badge]: https://img.shields.io/badge/docs-changelog-purple
[changelog]: https://github.com/deathbeds/jupyterlab-starters/tree/master/CHANGELOG.md
[ci-badge]: https://img.shields.io/azure-devops/build/nickbollweg/ec62cb62-c61a-4bf3-931c-089d81718737/8
[ci]: https://dev.azure.com/nickbollweg/deathbeds/_build/latest?definitionId=8&branchName=master
[conf]: https://github.com/deathbeds/jupyterlab-starters/tree/master/jupyter_server_config.json
[contributing]: https://github.com/deathbeds/jupyterlab-starters/tree/master/CONTRIBUTING.md
[cookiecutter]: https://github.com/cookiecutter/cookiecutter
[docs-badge]: https://readthedocs.org/projects/jupyterstarters/badge/?version=latest
[docs]: https://jupyterstarters.readthedocs.io/en/latest/?badge=latest
[jupyterlab-badge]: https://img.shields.io/badge/jupyterlab-1.x/2.x-orange?logo=jupyter
[launcher]: https://jupyterlab.readthedocs.io/en/stable/user/files.html#creating-files-and-activities
[license-badge]: https://img.shields.io/github/license/deathbeds/jupyterlab-starters
[license]: https://github.com/deathbeds/jupyterlab-starters/tree/master/LICENSE
[notebook-config]: https://jupyter-notebook.readthedocs.io/en/stable/config.html
[npm-badge]: https://img.shields.io/npm/v/@deathbeds/jupyterlab-starters
[npm]: https://www.npmjs.com/package/@deathbeds/jupyterlab-starters
[pypi-badge]: https://img.shields.io/pypi/v/jupyter-starters
[pypi]: https://pypi.org/project/jupyter-starters
[python-badge]: https://img.shields.io/badge/python-3.6+-blue?logo=python
[roadmap-badge]: https://img.shields.io/badge/docs-roadmap-purple
[roadmap]: https://github.com/deathbeds/jupyterlab-starters/tree/master/ROADMAP.md
[screenshot]: https://raw.githubusercontent.com/deathbeds/jupyterlab-starters/master/docs/screenshot.png
