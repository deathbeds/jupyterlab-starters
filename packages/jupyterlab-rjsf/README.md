# jupyterlab-rjsf

> [React JSON Schema Form][rjsf] for [JupyterLab][lab]

[rjsf]: https://github.com/rjsf-team/react-jsonschema-form
[lab]: https://github.com/jupyterlab/jupyterlab

## For users: Do I need to install this?

This project just provides some "glue" to be used by other JupyterLab extensions,
and other labextensions that use it should specify it as a `dependency` so it will
be installed for you, if needed.

### Related Projects

- [@deathbeds/jupyterlab-starters](https://github.com/deathbeds/jupyterlab-starters)
  uses this component in a sidebar to render things like cookiecutters and notebooks
  before making templated files

- [@deathbeds/wxyz-lab](https://github.com/deathbeds/jupyterlab-starters)
  uses an earlier version of this project to connect a JSON schema to the
  Jupyter Widgets ecosystem

## For Developers

### JupyterLab Extensions

Use the `SchemaForm`, a `@lumino/widget` that you can put inside of any
