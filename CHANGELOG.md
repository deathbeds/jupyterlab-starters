# CHANGELOG

## `jupyter_starters 1.0.1a0` (unreleased)

- [#51][] update of `@deathbeds/jupyterlab-rjsf` and `@deathbeds/jupyterlab-starters`.

## `@deathbeds/jupyterlab-starters 1.0.1a0` (unreleased)

- [#51][] uses new `@deathbeds/jupyterlab-rjsf` API

## `@deathbeds/jupyterlab-rjsf 1.0.1a0` (unreleased)

- [#51][] make more exports lazy loading

---

## `jupyter_starters 1.0.0a0`

- [#48][] support JupyterLab 3.x
  - it is now only necessary (and supported) to `pip` install this package
    to also install JupyterLab extensions
  - JupyterLab 1/2-style installation for user Lab Apps is no longer
    tested
  - for downstreams extensions, releases will continue on `npmjs.org`
    - versions sycned to the python package
    - on-going API support TBD

### Breaking changes

- due to upstream changes, the router URL has, for now, has changed from:
  - `/lab/tree/starter/<starter>/<path>` to
  - `?starter=<starter>/<path>`

## `@deathbeds/jupyterlab-rjsf 1.0.0a0`

- [#48][] support JupyterLab 3.x

## `@deathbeds/jupyterlab-starters 1.0.0a0`

- [#48][] support JupyterLab 3.x

---

## `jupyter_starters 0.6.0a0`

- [#45][] use new `@deathbeds/jupyterlab-starters 0.6.0a0`
- [#45][] be more specific on URL patterns

## `@deathbeds/jupyterlab-rjsf 0.6.0a0`

- [#45][] upgrade `@rjsf/core` for `anyOf` fixes
- [#45][] upgrade `react-codemirror2`

## `@deathbeds/jupyterlab-starters 0.6.0a0`

- [#45][] use new `@deathbeds/jupyterlab-rjsf 0.6.0a0`

---

## `jupyter_starters 0.5.0a0`

- [#41][] handle more recent cookiecutter metadata

## `@deathbeds/jupyterlab-rjsf 0.5.0a0`

- [#41][] upgrade `react-jsonschema-form` to `@rjsf/core`

## `@deathbeds/jupyterlab-starters 0.5.0a0`

- [#41][] upgrade `@deathbeds/jupyterlab-rjsf`

---

## `@deathbeds/jupyterlab-rjsf 0.4.0a0`

- [#38][] split out `rjsf` into its own package

## `@deathbeds/jupyterlab-starters 0.4.0a0`

- [#38][] depend on `@deathbeds/jupyterlab-rjsf`

## `jupyter_starters 0.4.0a0`

- Updated for parity with frontend

---

## `jupyter_starters 0.3.0a0`

- [#39][] adds listing and stopping of currently-running kernels to REST API

## `@deathbeds/jupyterlab-starters 0.3.0a0`

- [#39][] supports JupyterLab 2.0
- [#39][] adds listing and stopping of running kernel-backed starters

---

## `jupyter_starters 0.2.2a0`

- [#23][] rename `_json` module to `json_`, start documentation site in earnest

## `@deathbeds/jupyterlab-starters 0.2.2a0`

- [#29][] some updated class names based on schema
- [#34][] add stauts indicator for starting/continuing
- [#35][] add `/lab/tree/starter/<starter>/<path>` URL router

---

## `jupyter_starters 0.2.1a0`

- [#25][] add `py_src` for easier distribution of starters
- [#25][] add unit tests
- [#29][] handle minimally specified notebook metadata

## `@deathbeds/jupyterlab-starters 0.2.1a0`

- [#29][] handle minimally specified notebook metadata

---

## `jupyter_starters 0.2.0a0`

- [#13][] add notebook as starter
- [#18][] add copying files and commands while starter is continuing

## `@deathbeds/jupyterlab-starters 0.2.0a0`

- [#13][] add notebook metadata authoring
- [#17][] add Jupyter markdown to `title`, `description` and `ui:help` in schema forms
- [#18][] all starters launch in right sidebar
- [#21][] enable CodeMirror for JSON, Markdown, etc. editing

---

## `jupyter_starters 0.1.0a3`

- make optional dependency messages only appear in debug mode

--

## `jupyter_starters 0.1.0a2`

- add ignore patterns to schema
- fix default ignore patterns

## `@deathbeds/jupyterlab-starters 0.1.0a2`

- add glob ignore patterns to schema

---

## `jupyter_starters 0.1.0a1`

- add more sources of config

## `@deathbeds/jupyterlab-starters 0.1.0a0`

- initial implementation

## `jupyter_starters 0.1.0a0`

- initial implementation

[#13]: https://github.com/deathbeds/jupyterlab-starters/pull/13
[#17]: https://github.com/deathbeds/jupyterlab-starters/pull/17
[#18]: https://github.com/deathbeds/jupyterlab-starters/pull/18
[#21]: https://github.com/deathbeds/jupyterlab-starters/pull/21
[#23]: https://github.com/deathbeds/jupyterlab-starters/pull/23
[#25]: https://github.com/deathbeds/jupyterlab-starters/pull/25
[#29]: https://github.com/deathbeds/jupyterlab-starters/pull/29
[#34]: https://github.com/deathbeds/jupyterlab-starters/pull/34
[#35]: https://github.com/deathbeds/jupyterlab-starters/pull/35
[#38]: https://github.com/deathbeds/jupyterlab-starters/pull/38
[#39]: https://github.com/deathbeds/jupyterlab-starters/pull/39
[#41]: https://github.com/deathbeds/jupyterlab-starters/pull/41
[#45]: https://github.com/deathbeds/jupyterlab-starters/pull/45
[#48]: https://github.com/deathbeds/jupyterlab-starters/issues/48
[#51]: https://github.com/deathbeds/jupyterlab-starters/pull/51
