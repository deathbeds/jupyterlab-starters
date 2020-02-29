import * as React from 'react';

import {
  folderIcon,
  runIcon,
  circleIcon,
  stopIcon
} from '@jupyterlab/ui-components';

import { VDomRenderer } from '@jupyterlab/apputils';

import { CSS } from '../../css';

import { BuilderModel } from './model';

export class BuilderButtons extends VDomRenderer<BuilderModel> {
  constructor(model: BuilderModel) {
    super(model);
    this.addClass(CSS.BUILDER_BUTTONS);
  }

  protected render() {
    const m = this.model;
    const { context } = m;
    let path = context.cwd;
    path = path.startsWith('/') ? path : `/${path}`;
    path = path.endsWith('/') ? path : `${path}/`;
    path = path.replace(/\//g, ' / ');

    return (
      <>
        <footer>
          <label title={context.cwd}>
            <folderIcon.react tag="span" width="16" />
            {path}
          </label>
          <strong title={context.starter.description}>
            {context.starter.label}
          </strong>
        </footer>
        <section>
          {this.renderCancelButton()}
          {this.renderStartButton()}
        </section>
      </>
    );
  }

  protected renderCancelButton() {
    return (
      <button
        onClick={this.onDone}
        className={`${CSS.JP.styled} ${CSS.JP.reject}`}
      >
        <i className={`${CSS.JP.icon16} ${CSS.JP.ICON_CLASS.close}`}></i>
        <label> CANCEL</label>
      </button>
    );
  }

  protected renderStartButton() {
    const { status, startCount } = this.model;

    let icon = stopIcon;
    let label = 'FIXME';
    let statusClass = CSS.JP.warn;

    switch (status) {
      case 'ready':
        icon = runIcon;
        label = startCount ? 'CONTINUE' : 'START';
        statusClass = CSS.JP.accept;
        break;
      case 'starting':
        icon = circleIcon;
        label = startCount > 1 ? 'CONTINUING' : 'STARTING';
        break;
      default:
        break;
    }

    return (
      <button
        disabled={status !== 'ready'}
        className={`${CSS.JP.styled} ${statusClass}`}
        onClick={this.onStart}
      >
        {icon.react({ tag: 'span', width: 16 })}
        <label> {label} </label>
      </button>
    );
  }

  onStart = () => this.model.onStart();
  onDone = () => this.model.onDone();
}
