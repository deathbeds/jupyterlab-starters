# Contributing to jupyter(lab)-starters

`jupyter-starters` and `jupyterlab-starters` are [open source](./LICENSE) software,
and all contributions conforming to good sense, good taste, and the
[Jupyter Code of Conduct][code-of-conduct] are welcome, and will be reviewed
by the contributors, time-permitting.

[code-of-conduct]: https://github.com/jupyter/governance/blob/master/conduct/code_of_conduct.md

## setting up

> _There are probably other ways, but I haven't tried them_

- Be on Linux/OSX
- Get [Miniforge or Mambaforge](https://github.com/conda-forge/miniforge/releases)
- Get [doit](https://pydoit.org)

```bash
conda install doit
```

```bash
doit
```

Now you should have a working Lab.

```bash
doit lab
```

Try out some stuff. Make some whitepapers and cookiecutters.

## linting

```bash
doit lint
```

## testing

```bash
doit atest
```

> _You may want to run against a "clean" lab, e.g. `doit`_

## hacking

```bash
doit watch:lab
```

...in another terminal

```bash
doit lab
```

## documenting

```bash
doit docs
```

...or watch for changes

```bash
doit watch:docs
```

## releasing

- Download and unpack the artifacts from CI into `dist`
- Make a GitHub release with all of the release artifacts
- Upload the releases
```bash
twine upload dist/*.whl dist/*.tar.gz
npm publish dist/*.tgz
```
