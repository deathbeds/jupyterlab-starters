import * as React from 'react';
import { JSONObject } from '@phosphor/coreutils';
import { Signal } from '@phosphor/signaling';
import { Widget, BoxLayout } from '@phosphor/widgets';
import { VDomModel, VDomRenderer } from '@jupyterlab/apputils';

import { IStarterManager, IStartContext } from './tokens';
import { SchemaForm } from './schemaform';

import { CSS } from './css';

export class BodyBuilder extends Widget {
  private _form: SchemaForm<JSONObject>;
  private _context: IStartContext;
  private _buttons: BuilderButtons;

  model: BodyBuilder.Model;

  constructor(options: BodyBuilder.IOptions) {
    super(options);
    this.model = new BodyBuilder.Model(options);
    this.model.done = () => this.dispose();
    this.layout = new BoxLayout();
    this._context = options.context;
    const { label } = this._context.starter;
    this.id = Private.nextId();
    this.addClass(CSS.BUILDER);
    this.title.label = label;
    this.title.iconClass = this.model.iconClass;

    this._form = new SchemaForm(this._context.starter.schema, {
      liveValidate: true,
      formData: this._context.body
    });
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

export namespace BodyBuilder {
  export interface IOptions extends Widget.IOptions {
    name: string;
    manager: IStarterManager;
    context: IStartContext;
  }

  export class Model extends VDomModel {
    private _context: IStartContext;

    private _form: SchemaForm.Model<JSONObject>;
    private _name: string;

    private _start: Signal<Model, IStartContext>;
    private _manager: IStarterManager;
    private _done: Function;

    constructor(options: IOptions) {
      super();
      this._context = options.context;
      this._manager = options.manager;
      this._name = options.name;
      this._start = new Signal<Model, IStartContext>(this);
    }

    get start() {
      return this._start;
    }

    get context() {
      return this._context;
    }

    set context(context) {
      this._context = context;
      this._form.schema = context.starter.schema;
      this._form.formData = context.body;
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
      this.stateChanged.emit(void 0);
    }

    private _change = () => {
      this.stateChanged.emit(void 0);
    };

    onStart() {
      if (this._form.errors && this._form.errors.length) {
        return;
      }
      this._start.emit({
        ...this._context,
        body: this._form.formData
      });
    }

    get done() {
      return this._done;
    }

    set done(done) {
      this._done = done;
    }

    onDone() {
      this._done && this._done();
    }

    get iconClass() {
      return this._manager.iconClass(this._name, this._context.starter);
    }
  }
}

export class BuilderButtons extends VDomRenderer<BodyBuilder.Model> {
  constructor(model: BodyBuilder.Model) {
    super();
    this.model = model;
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

namespace Private {
  let _nextId = 0;
  export function nextId() {
    return `id-jp-starters-${name}-${_nextId++}`;
  }
}
