# CHANGELOG

## `2.0.0`

### `jupyter_starters 2.0.0`

- [#86] adds new `content` starter for JSON-only definitions with Jinja templates
- [#86] updates schema to `v3`

### `@deathbeds/jupyterlab-starters 2.0.0`

- [#86] refactors starter providers, runners, and the router into separate plugins
- [#86] adds a settings-backed provider for `content` starters, compatible with
  [JupyterLite]
- [#78] adds `category` and `rank` to all starter metadata, for customizing launcher
- [#90] adds `starter-body` and `starter-form` URL parameters

### `@deathbeds/jupyterlab-rjsf 2.0.0`

- [#99] upgrade to `@rjsf/core 5.0.1`

[jupyterlite]: https://jupyterlite.readthedocs.io
[#78]: https://github.com/deathbeds/jupyterlab-starters/pulls/78
[#86]: https://github.com/deathbeds/jupyterlab-starters/pulls/86
[#90]: https://github.com/deathbeds/jupyterlab-starters/pulls/90
[#99]: https://github.com/deathbeds/jupyterlab-starters/pulls/99

## `1.1.0`

### `jupyter_starters 1.1.0`

- [#62] adds a CLI tool, `jupyter starters list` (with option `--json`)
- [#68] remove cookiecutter metadata parsing, as it no longer works consistently
- [#69] minimum python is now 3.7
- [#71] support cookiecutter 1.7.1 `directory` argument, `jupyter-server-proxy` example

### `@deathbeds/jupyterlab-starters 1.1.0`

### `@deathbeds/jupyterlab-rjsf 1.1.0`

- [#66] `formData` is now honored when constructing a form
- [#69] upgrade to `@rjsf/core` 3

[#62]: https://github.com/deathbeds/jupyterlab-starters/issues/62
[#66]: https://github.com/deathbeds/jupyterlab-starters/issues/66
[#68]: https://github.com/deathbeds/jupyterlab-starters/issues/68
[#69]: https://github.com/deathbeds/jupyterlab-starters/pulls/69
[#71]: https://github.com/deathbeds/jupyterlab-starters/pulls/71

## `1.0.2`

### `jupyter_starters 1.0.2`

- [#54] adapt kernel shutdown to newer `jupyter_client >=6.1` API

### `@deathbeds/jupyterlab-starters 1.0.2`

### `@deathbeds/jupyterlab-rjsf 1.0.2`

- [#56] upgrade to `@rjsf/core 2.5.1`

[#54]: https://github.com/deathbeds/jupyterlab-starters/pull/54
[#56]: https://github.com/deathbeds/jupyterlab-starters/pull/56

## `1.0.1a0`

### `jupyter_starters 1.0.1a0`

- [#51] update of `@deathbeds/jupyterlab-rjsf` and `@deathbeds/jupyterlab-starters`.

### `@deathbeds/jupyterlab-starters 1.0.1a0`

- [#51] uses new `@deathbeds/jupyterlab-rjsf` API

### `@deathbeds/jupyterlab-rjsf 1.0.1a0`

- [#51] make more exports lazy loading

[#51]: https://github.com/deathbeds/jupyterlab-starters/pull/51

## `1.0.0a0`

### `jupyter_starters 1.0.0a0`

- [#48] support JupyterLab 3.x
  - it is now only necessary (and supported) to `pip` install this package to also
    install JupyterLab extensions
  - JupyterLab 1/2-style installation for user Lab Apps is no longer tested
  - for downstreams extensions, releases will continue on `npmjs.org`
    - versions sycned to the python package
    - on-going API support TBD

#### Breaking changes

- due to upstream changes, the router URL has, for now, has changed from:
  - `/lab/tree/starter/<starter>/<path>` to
  - `?starter=<starter>/<path>`

### `@deathbeds/jupyterlab-rjsf 1.0.0a0`

- [#48] support JupyterLab 3.x

### `@deathbeds/jupyterlab-starters 1.0.0a0`

- [#48] support JupyterLab 3.x

[#48]: https://github.com/deathbeds/jupyterlab-starters/issues/48

## `0.6.0a0`

### `jupyter_starters 0.6.0a0`

- [#45] use new `@deathbeds/jupyterlab-starters 0.6.0a0`
- [#45] be more specific on URL patterns

### `@deathbeds/jupyterlab-rjsf 0.6.0a0`

- [#45] upgrade `@rjsf/core` for `anyOf` fixes
- [#45] upgrade `react-codemirror2`

### `@deathbeds/jupyterlab-starters 0.6.0a0`

- [#45] use new `@deathbeds/jupyterlab-rjsf 0.6.0a0`

[#45]: https://github.com/deathbeds/jupyterlab-starters/pull/45

## `0.5.0a0`

### `jupyter_starters 0.5.0a0`

- [#41] handle more recent cookiecutter metadata

### `@deathbeds/jupyterlab-rjsf 0.5.0a0`

- [#41] upgrade `react-jsonschema-form` to `@rjsf/core`

### `@deathbeds/jupyterlab-starters 0.5.0a0`

- [#41] upgrade `@deathbeds/jupyterlab-rjsf`

[#41]: https://github.com/deathbeds/jupyterlab-starters/pull/41

## `0.4.0a0`

### `@deathbeds/jupyterlab-rjsf 0.4.0a0`

- [#38] split out `rjsf` into its own package

### `@deathbeds/jupyterlab-starters 0.4.0a0`

- [#38] depend on `@deathbeds/jupyterlab-rjsf`

### `jupyter_starters 0.4.0a0`

- Updated for parity with frontend

## `0.3.0a0`

### `jupyter_starters 0.3.0a0`

- [#39] adds listing and stopping of currently-running kernels to REST API

### `@deathbeds/jupyterlab-starters 0.3.0a0`

- [#39] supports JupyterLab 2.0
- [#39] adds listing and stopping of running kernel-backed starters

[#38]: https://github.com/deathbeds/jupyterlab-starters/pull/38
[#39]: https://github.com/deathbeds/jupyterlab-starters/pull/39

## `0.2.2a0`

### `jupyter_starters 0.2.2a0`

- [#23] rename `_json` module to `json_`, start documentation site in earnest

### `@deathbeds/jupyterlab-starters 0.2.2a0`

- [#29] some updated class names based on schema
- [#34] add stauts indicator for starting/continuing
- [#35] add `/lab/tree/starter/<starter>/<path>` URL router

[#23]: https://github.com/deathbeds/jupyterlab-starters/pull/23
[#34]: https://github.com/deathbeds/jupyterlab-starters/pull/34
[#35]: https://github.com/deathbeds/jupyterlab-starters/pull/35

## `0.2.1a0`

### `jupyter_starters 0.2.1a0`

- [#25] add `py_src` for easier distribution of starters
- [#25] add unit tests
- [#29] handle minimally specified notebook metadata

### `@deathbeds/jupyterlab-starters 0.2.1a0`

- [#29] handle minimally specified notebook metadata

[#25]: https://github.com/deathbeds/jupyterlab-starters/pull/25
[#29]: https://github.com/deathbeds/jupyterlab-starters/pull/29

## `0.2.0a0`

### `jupyter_starters 0.2.0a0`

- [#13] add notebook as starter
- [#18] add copying files and commands while starter is continuing

### `@deathbeds/jupyterlab-starters 0.2.0a0`

- [#13] add notebook metadata authoring
- [#17] add Jupyter markdown to `title`, `description` and `ui:help` in schema forms
- [#18] all starters launch in right sidebar
- [#21] enable CodeMirror for JSON, Markdown, etc. editing

[#13]: https://github.com/deathbeds/jupyterlab-starters/pull/13
[#17]: https://github.com/deathbeds/jupyterlab-starters/pull/17
[#18]: https://github.com/deathbeds/jupyterlab-starters/pull/18
[#21]: https://github.com/deathbeds/jupyterlab-starters/pull/21

## `0.1.0a3`

### `jupyter_starters 0.1.0a3`

- make optional dependency messages only appear in debug mode

## `0.1.0a2`

### `jupyter_starters 0.1.0a2`

- add ignore patterns to schema
- fix default ignore patterns

### `@deathbeds/jupyterlab-starters 0.1.0a2`

- add glob ignore patterns to schema

## `0.1.0a1`

### `jupyter_starters 0.1.0a1`

- add more sources of config

### `@deathbeds/jupyterlab-starters 0.1.0a0`

- initial implementation

### `jupyter_starters 0.1.0a0`

- initial implementation
