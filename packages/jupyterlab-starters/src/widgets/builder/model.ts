import { JSONObject } from '@lumino/coreutils';
import { Signal } from '@lumino/signaling';
import { Widget } from '@lumino/widgets';
import { VDomModel } from '@jupyterlab/apputils';

import { IStarterManager, IStartContext } from '../../tokens';

import { SchemaFormModel } from '@deathbeds/jupyterlab-rjsf/lib/schemaform/model';

export class BuilderModel extends VDomModel {
  private _context: IStartContext;

  private _form: SchemaFormModel<JSONObject>;
  private _name: string;
  private _status: BuilderModel.TStatus = 'starting';

  private _start: Signal<BuilderModel, IStartContext>;
  private _manager: IStarterManager;
  private _done: Function;
  private _startCount = 0;

  constructor(options: BuilderModel.IOptions) {
    super();
    this._context = options.context;
    this._manager = options.manager;
    this._name = options.name;
    this._start = new Signal<BuilderModel, IStartContext>(this);
  }

  get startCount() {
    return this._startCount;
  }

  get status() {
    if (!this._form) {
      return 'starting';
    } else if (this._form.errors.length || this._form.errorsObserved) {
      return 'error';
    }
    return this._status;
  }

  set status(status) {
    this._status = status;
    this.stateChanged.emit(void 0);
  }

  get start() {
    return this._start;
  }

  get manager() {
    return this._manager;
  }

  get context() {
    return this._context;
  }

  set context(context) {
    this._context = context;
    this._form.schema = context.starter.schema;
    this._form.formData = context.body;
    this._form.uiSchema = context.starter.uiSchema;
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
    if (this._form.errors && this._form.errors.length) {
      this.status = 'error';
    } else {
      this.status = 'ready';
    }
    this.stateChanged.emit(void 0);
  };

  onStart() {
    if (this._form.errors && this._form.errors.length) {
      return;
    }
    this._startCount += 1;
    this.status = 'starting';
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

  get icon() {
    return this._manager.icon(this._name, this._context.starter);
  }
}

export namespace BuilderModel {
  export interface IOptions extends Widget.IOptions {
    name: string;
    manager: IStarterManager;
    context: IStartContext;
  }

  export type TStatus = 'ready' | 'starting' | 'error';
}
