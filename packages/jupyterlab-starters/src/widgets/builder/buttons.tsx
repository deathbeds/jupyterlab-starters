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
