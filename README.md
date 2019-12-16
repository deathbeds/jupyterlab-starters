# jupyterlab-starters

> _Parameterized file and directory starters for JupyterLab._

[![badge-binder][]][binder] [![badge-ci][]][ci] [![pypi-badge][]][pypi] [![npm-badge][]][npm]
[![roadmap-badge][]][roadmap] [![changelog-badge][]][changelog] ![python-badge][] ![jupyterlab-badge][] [![license-badge][]][license]

![screenshot][]

## What's a starter?

- [x] A single file
- [x] A directory
- [x] A python function
- [x] A [cookiecutter][]
- [ ] A shell script

... that shows up in your JupyterLab at the click of a button

## Installing

> _You'll need `jupyterlab >=1,<2`, `python >=3.6`, and `nodejs >=8`_

```bash
pip install --pre jupyter_starters
jupyter labextension install @deathbeds/jupyterlab-starters
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

> _more docs TBD: for now, see examples in [jupyter_notebook_config.json](./jupyter_notebook_config.json)_

## Alternatives

Don't like what you see here? Try these other approaches:

- [jupyterlab_templates](https://github.com/timkpaine/jupyterlab_templates)

[badge-binder]: https://mybinder.org/badge_logo.svg
[badge-ci]: https://dev.azure.com/nickbollweg/deathbeds/_apis/build/status/deathbeds.jupyterlab-starters?branchName=master
[binder]: https://mybinder.org/v2/gh/deathbeds/jupyterlab-starters/master?urlpath=lab
[ci]: https://dev.azure.com/nickbollweg/deathbeds/_build/latest?definitionId=8&branchName=master
[cookiecutter]: https://github.com/cookiecutter/cookiecutter
[notebook-config]: https://jupyter-notebook.readthedocs.io/en/stable/config.html
[launcher]: https://jupyterlab.readthedocs.io/en/stable/user/files.html#creating-files-and-activities
[license-badge]: https://img.shields.io/github/license/deathbeds/jupyterlab-starters
[roadmap-badge]: https://img.shields.io/badge/docs-roadmap-purple
[changelog-badge]: https://img.shields.io/badge/docs-changelog-purple
[jupyterlab-badge]: https://img.shields.io/badge/jupyterlab-1.x-orange?logo=jupyter
[python-badge]: https://img.shields.io/badge/python-3.6+-blue?logo=python
[roadmap]: https://github.com/deathbeds/jupyterlab-starters/tree/master/ROADMAP.md
[changelog]: https://github.com/deathbeds/jupyterlab-starters/tree/master/CHANGELOG.md
[contributing]: https://github.com/deathbeds/jupyterlab-starters/tree/master/CONTRIBUTING.md
[license]: https://github.com/deathbeds/jupyterlab-starters/tree/master/LICENSE
[screenshot]: https://raw.githubusercontent.com/deathbeds/jupyterlab-starters/master/docs/screenshot.png
[pypi-badge]: https://img.shields.io/pypi/v/jupyter-starters
[pypi]: https://pypi.org/project/jupyter-starters
[npm-badge]: https://img.shields.io/npm/v/deathbeds/jupyterlab-starters
[npm]: https://www.npmjs.com/package/@deathbeds/jupyterlab-starters
