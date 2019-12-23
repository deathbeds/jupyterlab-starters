import * as React from 'react';
import { JSONObject } from '@phosphor/coreutils';
import { Widget, BoxLayout } from '@phosphor/widgets';
import { VDomRenderer } from '@jupyterlab/apputils';

import { IStartContext } from '../../tokens';
import { CSS } from '../../css';

import { SchemaForm } from '../schemaform';

import { BuilderModel } from './model';

export class BodyBuilder extends Widget {
  private _form: SchemaForm<JSONObject>;
  private _context: IStartContext;
  private _buttons: BuilderButtons;

  model: BuilderModel;

  constructor(options: BuilderModel.IOptions) {
    super(options);
    this.model = new BuilderModel(options);
    this.model.done = () => this.dispose();
    this.layout = new BoxLayout();
    this._context = options.context;
    const { label } = this._context.starter;
    this.id = Private.nextId();
    this.addClass(CSS.BUILDER);
    this.addClass(CSS.FORM_PANEL);
    this.title.label = label;
    this.title.iconClass = this.model.iconClass;

    this._form = new SchemaForm(
      this._context.starter.schema,
      {
        liveValidate: true,
        formData: this._context.body,
        uiSchema: this._context.starter.uiSchema || {}
      },
      { markdown: this.model.manager.markdown }
    );

    this._buttons = this.makeButtons();

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

    buttons.model.form = this._form.model;

    return buttons;
  }
}

export class BuilderButtons extends VDomRenderer<BuilderModel> {
  constructor(model: BuilderModel) {
    super();
    this.model = model;
    this.addClass(CSS.BUILDER_BUTTONS);
  }

  protected render() {
    const { form } = this.model;
    const hasErrors = !!(!form || form.errors.length || form.errorsObserved);

    return (
      <div>
        <button
          onClick={this.onDone}
          className={`${CSS.JP.styled} ${CSS.JP.warn}`}
        >
          CANCEL
        </button>
        <button
          disabled={hasErrors}
          className={`${hasErrors ? '' : CSS.JP.accept} ${CSS.JP.styled}`}
          onClick={this.onStart}
        >
          START
        </button>
      </div>
    );
  }

  onStart = () => this.model.onStart();
  onDone = () => this.model.onDone();
}

namespace Private {
  let _nextId = 0;
  export function nextId() {
    return `id-jp-starters-${name}-${_nextId++}`;
  }
}
