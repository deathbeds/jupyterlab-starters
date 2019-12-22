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
    const { starter, iconURI } = this.model;

    if (!starter) {
      return <div className={CSS.LAUNCHER.CARD}></div>;
    }

    return (
      <div className={CSS.LAUNCHER.CARD} title={starter.description}>
        <div className={CSS.LAUNCHER.ICON}>
          <img src={iconURI} />
        </div>

        <div className={CSS.LAUNCHER.LABEL}>
          <p>{starter.label}</p>
        </div>
      </div>
    );
  }
}
