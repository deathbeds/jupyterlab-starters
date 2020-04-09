# jupyterlab-rjsf

> [React JSON Schema Form][rjsf] for [JupyterLab][lab]

[rjsf]: https://github.com/rjsf-team/react-jsonschema-form
[lab]: https://github.com/jupyterlab/jupyterlab

## For users: Do I need to install this?

For now, this project just provides some "glue" to be used by other JupyterLab extensions,
and other labextensions that use it should specify it as a `dependency` so it will
be installed for you, if needed.

> A follow-on release will add more tightly-integrated Document (a la `Notebook`)
> with a `MimeRenderer` for working with JSON instances, JSON Schema, and
> `rjsf''s UI Schema, with support for alternate encodings like YAML and JSONL.
> See more in the [roadmap](#Roadmap).

### Related Projects

Things you can `jupyter labextension install` to use this component:

- [@deathbeds/jupyterlab-starters](https://github.com/deathbeds/jupyterlab-starters)
  uses this component in a sidebar to render things like cookiecutters and notebooks
  before making templated files

  - the tests for this component are also mostly contained in this repo, for now

- [@deathbeds/wxyz](https://github.com/deathbeds/wxyz)
  uses an earlier version of this component to connect a JSON Schema to the
  broader Jupyter Widgets ecosystem, but also works with other `wxyz` widgets without
  a "server" kernel.

## For Developers

### JupyterLab Extensions

Use the `SchemaForm`, a `@lumino/widget` that you can put inside of any other
widget (such as the `DockPanel`). It's `model` exposes the `schema`, `formData`,
other `rjsf` specifics, and can be connected to with `model.stateChanged`.

### React

Several underlying libraries are used from the broader React ecosystem.

> `rjsf` in particular has a large pending release (2.x), so some APIs are subject
> to change abruptly in the near future.

> > TBD: more info on `async-component`, and `rjsf`-specifics like `jsonobject`
> > and `codemirror`, `Form` and `Theme`

## Roadmap

- [ ] `MimeRenderer`
- [ ] `Document`
  - [ ] JSON Instance as form
  - [ ] JSON Schema as form?
  - [ ] `rjsf` UI schema
  - [ ] formatting
- - [ ] `rjsf` 2.x
- [ ] additional extension points
  - [ ] readers e.g. `YAML`, `JSONL`, `TOML`
- [ ] explore additional form libraries, e.g. `formik`
