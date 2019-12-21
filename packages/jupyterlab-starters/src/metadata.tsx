import * as React from 'react';
import { JSONObject } from '@phosphor/coreutils';
import { Widget, BoxLayout } from '@phosphor/widgets';
import { VDomModel, VDomRenderer } from '@jupyterlab/apputils';

import * as SCHEMA_DEFAULT from './schema.json';

export const NOTEBOOK_META_KEY = 'jupyter_starters';
export const NOTEBOOK_META_SUBKEY = 'starter';

import { IStarterManager } from './tokens';
import { SchemaForm } from './schemaform';

import { CSS } from './css';
import { NotebookPanel } from '@jupyterlab/notebook';

const JSON_SCHEMA = (SCHEMA_DEFAULT as any).default;

const { definitions } = JSON_SCHEMA;

const starterMeta = definitions['starter-meta'];

let STARTER_META = {
  definitions,
  type: 'object',
  ...starterMeta
};

delete STARTER_META['required'];

export class NotebookMetadata extends Widget {
  private _form: SchemaForm<JSONObject>;
  private _buttons: BuilderButtons;

  model: NotebookMetadata.Model;

  constructor(options: NotebookMetadata.IOptions) {
    super(options);
    this.model = new NotebookMetadata.Model();
    this.layout = new BoxLayout();
    this.id = Private.nextId();
    this.addClass(CSS.META);
    this.addClass(CSS.FORM_PANEL);

    this._form = new SchemaForm(STARTER_META, { liveValidate: true });
    this._buttons = this.makeButtons();
    this.model.form = this._form.model;

    this.boxLayout.addWidget(this._form);
    this.boxLayout.addWidget(this._buttons);
  }

  get boxLayout() {
    return this.layout as BoxLayout;
  }

  dispose() {
    super.dispose();
    if (!this.isDisposed) {
      this.model.dispose();
    }
  }

  makeButtons() {
    const buttons = new BuilderButtons(this.model);
    return buttons;
  }
}

export namespace NotebookMetadata {
  export interface IOptions extends Widget.IOptions {
    manager: IStarterManager;
  }

  export class Model extends VDomModel {
    private _form: SchemaForm.Model<JSONObject>;
    private _notebook: NotebookPanel;

    get notebook() {
      return this._notebook;
    }

    set notebook(notebook) {
      if (this._notebook) {
        this._notebook.model.metadata.changed.disconnect(
          this.onNotebookMeta,
          this
        );
      }

      this._notebook = notebook;

      if (this._notebook) {
        this._notebook.model.metadata.changed.connect(
          this.onNotebookMeta,
          this
        );
        this.onNotebookMeta();
      }
      this.stateChanged.emit(void 0);
    }

    onNotebookMeta() {
      const fromNotebook = this._notebook.model.metadata.get(
        NOTEBOOK_META_KEY
      ) as JSONObject;
      console.log('getting metadata', fromNotebook);
      if (fromNotebook && fromNotebook[NOTEBOOK_META_SUBKEY]) {
        this._form.formData = fromNotebook[NOTEBOOK_META_SUBKEY] as JSONObject;
      }
    }

    get form() {
      return this._form;
    }

    set form(form) {
      if (this._form) {
        this._form.stateChanged.disconnect(this._change, this);
      }
      this._form = form;
      form.stateChanged.connect(this._change, this);
      this._change();
    }

    private _change = () => {
      const { formData } = this._form;
      console.log('setting metadata', formData);
      if (this._notebook && formData) {
        const fromNotebook =
          this._notebook.model.metadata.get(NOTEBOOK_META_KEY) || ({} as any);
        const nbStarter = fromNotebook[NOTEBOOK_META_SUBKEY] || {};
        this._notebook.model.metadata.set(NOTEBOOK_META_KEY, {
          ...fromNotebook,
          [NOTEBOOK_META_SUBKEY]: {
            ...nbStarter,
            ...formData
          }
        });
      }
      this.stateChanged.emit(void 0);
    };
  }
}

export class BuilderButtons extends VDomRenderer<NotebookMetadata.Model> {
  constructor(model: NotebookMetadata.Model) {
    super();
    this.model = model;
    this.addClass(CSS.BUILDER_BUTTONS);
  }

  protected render() {
    const { form } = this.model;
    const hasErrors = !!(!form || form.errors.length || form.errorsObserved);

    return (
      <div>
        <button className={`${CSS.JP.styled} ${CSS.JP.warn}`}>CANCEL</button>
        <button
          disabled={hasErrors}
          className={`${hasErrors ? '' : CSS.JP.accept} ${CSS.JP.styled}`}
        >
          START
        </button>
      </div>
    );
  }
}

namespace Private {
  let _nextId = 0;
  export function nextId() {
    return `id-jp-starters-notebook-${name}-${_nextId++}`;
  }
}
