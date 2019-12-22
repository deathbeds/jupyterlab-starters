import { VDomModel } from '@jupyterlab/apputils';

import * as SCHEMA from '../../_schema';
import { CSS } from '../../css';

export class PreviewCardModel extends VDomModel {
  private _starter: SCHEMA.Starter;

  constructor(options: PreviewCardModel.IOptions = {}) {
    super();
    this._starter = options.starter;
  }

  get iconURI() {
    const icon = this._starter?.icon || CSS.SVG.DEFAULT_ICON;
    return `data:image/svg+xml;base64,${btoa(icon)}`;
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
