import * as React from 'react';

import { VDomRenderer } from '@jupyterlab/apputils';

import { CSS } from '../../css';

import { BuilderModel } from './model';

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
      <>
        <div>
          <strong title={this.model.context.starter.description}>
            {this.model.context.starter.label}
          </strong>
          <br />
          <label title={this.model.context.cwd}>
            {this.model.manager.icons.iconReact({
              name: 'folder',
              width: 16
            })}
            {`/ ${this.model.context.cwd.replace('/', ' / ')}`}
          </label>
        </div>
        <button
          onClick={this.onDone}
          className={`${CSS.JP.styled} ${CSS.JP.warn}`}
        >
          {this.model.manager.icons.iconReact({
            name: 'stop',
            width: 16
          })}
          <label> CANCEL</label>
        </button>
        <button
          disabled={hasErrors}
          className={`${hasErrors ? '' : CSS.JP.accept} ${CSS.JP.styled}`}
          onClick={this.onStart}
        >
          {this.model.manager.icons.iconReact({
            name: 'run',
            width: 16
          })}
          <label> START</label>
        </button>
      </>
    );
  }

  onStart = () => this.model.onStart();
  onDone = () => this.model.onDone();
}
