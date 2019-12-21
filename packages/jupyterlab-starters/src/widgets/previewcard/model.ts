import { VDomModel } from '@jupyterlab/apputils';

import * as SCHEMA from '../../_schema';

export class PreviewCardModel extends VDomModel {
  private _starter: SCHEMA.Starter;

  constructor(options: PreviewCardModel.IOptions = {}) {
    super();
    this._starter = options.starter;
  }

  get starter() {
    return this._starter;
  }

  set starter(starter) {
    this._starter = starter;
    this.stateChanged.emit(void 0);
  }
}

export namespace PreviewCardModel {
  export interface IOptions {
    starter?: SCHEMA.Starter;
  }
}
