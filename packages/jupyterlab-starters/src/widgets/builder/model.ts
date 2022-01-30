import { JSONObject } from '@lumino/coreutils';
import { ISignal, Signal } from '@lumino/signaling';
import { Widget } from '@lumino/widgets';
import { VDomModel } from '@jupyterlab/apputils';
import type { LabIcon } from '@jupyterlab/ui-components';

import { IStarterManager, IStartContext } from '../../tokens';

import { SchemaFormModel } from '@deathbeds/jupyterlab-rjsf';

export class BuilderModel extends VDomModel {
  private _context: IStartContext;

  private _form: SchemaFormModel<JSONObject>;
  private _name: string;
  private _status: BuilderModel.TStatus = 'starting';

  private _start: Signal<BuilderModel, IStartContext>;
  private _manager: IStarterManager;
  private _done: BuilderModel.TDoneCallback;
  private _startCount = 0;

  constructor(options: BuilderModel.IOptions) {
    super();
    this._context = options.context;
    this._manager = options.manager;
    this._name = options.name;
    this._start = new Signal<BuilderModel, IStartContext>(this);
  }

  get startCount(): number {
    return this._startCount;
  }

  get status(): BuilderModel.TStatus {
    if (!this._form) {
      return 'starting';
    } else if (this._form.errors.length || this._form.errorsObserved) {
      return 'error';
    }
    return this._status;
  }

  set status(status: BuilderModel.TStatus) {
    this._status = status;
    this.stateChanged.emit(void 0);
  }

  get start(): ISignal<BuilderModel, IStartContext> {
    return this._start;
  }

  get manager(): IStarterManager {
    return this._manager;
  }

  get context(): IStartContext {
    return this._context;
  }

  set context(context: IStartContext) {
    this._context = context;
    this._form.schema = context.starter.schema || {};
    this._form.formData = context.body;
    this._form.uiSchema = context.starter.uiSchema;
  }

  get form(): SchemaFormModel<JSONObject> {
    return this._form;
  }

  set form(form: SchemaFormModel<JSONObject>) {
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

  onStart(): void {
    if (this._form.errors && this._form.errors.length) {
      return;
    }
    this._startCount += 1;
    this.status = 'starting';
    this._start.emit({
      ...this._context,
      body: this._form.formData,
    });
  }

  get done(): BuilderModel.TDoneCallback {
    return this._done;
  }

  set done(done: BuilderModel.TDoneCallback) {
    this._done = done;
  }

  onDone(): void {
    this._done && this._done();
  }

  get icon(): LabIcon.ILabIcon {
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

  export type TDoneCallback = () => void;
}
