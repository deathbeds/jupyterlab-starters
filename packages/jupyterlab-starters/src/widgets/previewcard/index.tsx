import * as React from 'react';
import { VDomRenderer } from '@jupyterlab/apputils';
import { CSS } from '../../css';

import { PreviewCardModel } from './model';

export class PreviewCard extends VDomRenderer<PreviewCardModel> {
  constructor(options: PreviewCardModel.IOptions = {}) {
    super();
    this.model = new PreviewCardModel(options);
    this.addClass(CSS.PREVIEW);
  }

  render() {
    const m = this.model;

    const { starter, iconURI } = m;

    if (!starter) {
      return (
        <div>
          <div className={CSS.LAUNCHER.CARD}></div>
        </div>
      );
    }

    return (
      <div>
        <div className={CSS.LAUNCHER.CARD} title={starter.description}>
          <div className={CSS.LAUNCHER.ICON}>
            <img src={iconURI} />
          </div>

          <div className={CSS.LAUNCHER.LABEL}>
            <p>{starter.label}</p>
          </div>
        </div>
      </div>
    );
  }
}
