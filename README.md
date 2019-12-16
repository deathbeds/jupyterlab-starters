# jupyterlab-starters

> _Parameterized file and directory starters for JupyterLab._

[![badge-binder][]][binder] [![badge-ci][]][ci] [![license][]](./LICENSE)

## What's a starter?

- [x] A single file
- [x] A directory
- [x] A python function
- [x] A [cookiecutter][]
- [ ] A shell script

... that shows up in your JupyterLab at the click of a button

## Installing

> _TBD: for the time being, try a [development install](./CONTRIBUTING.md)._

## Configuring

Like the Jupyter Notebook server, JupyterHub and other Jupyter interactive computing
tools, `jupyter-starters` can be configured via [Python or JSON files][notebook-config]
in _well-known locations_. You can find out where to put them on your system with:

```bash
jupyter --paths
```

They will be merged from bottom to top, and the directory where you launch your
`notebook` server wins, making it easy to check in to version control.

The very simplest is `copy`, which will copy a file or folder to the location
it is launched from in the JupyterLab [Launcher][].

```yaml
{
  'StarterManager':
    {
      'extra_starters':
        {
          'whitepaper-single':
            {
              'type': 'copy',
              'label': 'Whitepaper Notebook',
              'description': 'A reusable notebook for proposing research',
              'src': 'examples/whitepaper-single.ipynb',
            },
        },
    },
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
[license]: https://img.shields.io/github/license/deathbeds/jupyterlab-starters
