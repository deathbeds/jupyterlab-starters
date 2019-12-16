# Contributing to jupyter(lab)-starters

`jupyter-starters` and `jupyterlab-starters` are [open source](./LICENSE) software,
and all contributions conforming to good sense, good taste, and the
[Jupyter Code of Conduct][code-of-conduct] are welcome, and will be reviewed
by the contributors, time-permitting.

[code-of-conduct]: https://github.com/jupyter/governance/blob/master/conduct/code_of_conduct.md

## setting up

> _There are probably other ways, but I haven't tried them_

- Be on Linux/OSX
- Get [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- Get [anaconda-project](https://github.com/Anaconda-Platform/anaconda-project)
  - `anaconda-project` is a lot to type
  - go ahead and add
    ```bash
    alias "apr=anaconda-project run"
    ```
    to your `.<your shell>rc`

```bash
anaconda-project run postBuild
```

Now you have a working Lab.

```bash
anaconda-project run lab
```

Try out some stuff. Make some whitepapers and cookiecutters.

## testing

```bash
anaconda-project run atest
```

> _You have to run against a "clean" lab, e.g. `postBuild`_

## hacking

```bash
anaconda-project run jlpm watch
```

...and in another terminal

```bash
anaconda-project run lab --watch
```

> _You'll have to restart lab if you add files_

## linting

```bash
anaconda-project run lint
```

## releasing

```bash
anaconda-project run release
anaconda-project run upload
```
