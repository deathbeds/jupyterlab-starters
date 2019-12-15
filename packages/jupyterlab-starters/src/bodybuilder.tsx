import * as React from 'react';
import { JSONObject } from '@phosphor/coreutils';
import { Signal } from '@phosphor/signaling';
import { Widget, BoxLayout } from '@phosphor/widgets';
import { VDomModel, VDomRenderer } from '@jupyterlab/apputils';

import { IStarterManager, DEFAULT_ICON_CLASS, IStartContext } from './tokens';
import { SchemaForm } from './schemaform';

import { CSS } from './css';

export class BuilderButtons extends VDomRenderer<BuilderButtons.Model> {
  constructor() {
    super();
    this.model = new BuilderButtons.Model();
    this.addClass(CSS.BUILDER_BUTTONS);
  }

  protected render() {
    const hasErrors = (this.model.form?.errors || []).length > 0;

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

export namespace BuilderButtons {
  export class Model extends VDomModel {
    start = () => {
      // no-op
    };
    preview = () => {
      // no-op
    };
    done = () => {
      // no-op
    };

    private _form: SchemaForm.Model<JSONObject>;

    get form() {
      return this._form;
    }

    set form(form) {
      this._form = form;
      form.stateChanged.connect(() => this.stateChanged.emit(void 0));
      this.stateChanged.emit(void 0);
    }

    onStart() {
      this.start();
    }

    onDone() {
      this.done();
    }

    onPreview() {
      this.preview();
    }
  }
}

export class BodyBuilder extends Widget {
  private _start: Signal<BodyBuilder, IStartContext>;
  private _form: SchemaForm<JSONObject>;
  private _context: IStartContext;
  private _buttons: BuilderButtons;

  constructor(options: BodyBuilder.IOptions) {
    super(options);
    this.layout = new BoxLayout();
    this._context = options.context;
    this._start = new Signal<BodyBuilder, IStartContext>(this);
    const { label, icon } = this._context.starter;
    this.id = Private.nextId();
    this.addClass(CSS.BUILDER);
    this.title.label = label;
    this.title.iconClass = icon || DEFAULT_ICON_CLASS;

    this._form = new SchemaForm(this._context.starter.schema, {
      liveValidate: true
    });
    this._buttons = this.makeButtons();

    this.boxLayout.addWidget(this._buttons);
    this.boxLayout.addWidget(this._form);
  }

  get boxLayout() {
    return this.layout as BoxLayout;
  }

  makeButtons() {
    const buttons = new BuilderButtons();

    buttons.model.form = this._form.model;

    buttons.model.start = () => {
      const value = this._form.getValue();
      if (value.errors && value.errors.length) {
        return;
      }
      this._start.emit({
        ...this._context,
        body: value.formData
      });
    };

    buttons.model.done = () => this.dispose();

    return buttons;
  }

  get start() {
    return this._start;
  }
}

export namespace BodyBuilder {
  export interface IOptions extends Widget.IOptions {
    manager: IStarterManager;
    context: IStartContext;
  }
}

namespace Private {
  let _nextId = 0;
  export function nextId() {
    return `id-jp-starters-${name}-${_nextId++}`;
  }
}
