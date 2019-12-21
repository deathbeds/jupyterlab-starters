import * as React from 'react';

import { JSONObject } from '@phosphor/coreutils';
import { Widget, BoxLayout } from '@phosphor/widgets';
import { VDomRenderer } from '@jupyterlab/apputils';

import { CSS } from '../../css';
import { SchemaForm } from '../schemaform';
import { NotebookMetadataModel } from './model';

export class NotebookMetadata extends Widget {
  private _form: SchemaForm<JSONObject>;
  private _buttons: BuilderButtons;

  model: NotebookMetadataModel;

  constructor(options: NotebookMetadataModel.IOptions) {
    super(options);
    this.model = new NotebookMetadataModel(options);
    this.layout = new BoxLayout();
    this.id = Private.nextId();
    this.addClass(CSS.META);
    this.addClass(CSS.FORM_PANEL);

    this._form = new SchemaForm(this.model.liveSchema, { liveValidate: true });
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

export class BuilderButtons extends VDomRenderer<NotebookMetadataModel> {
  constructor(model: NotebookMetadataModel) {
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
