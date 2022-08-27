import { Clipboard, VDomRenderer, VDomModel } from '@jupyterlab/apputils';
import { copyIcon, LabIcon, checkIcon } from '@jupyterlab/ui-components';
import * as React from 'react';

import { CSS } from '../../css';
import {
  STARTER_BODY_PARAM,
  STARTER_FORM_PARAM,
  STARTER_NAME_PARAM,
} from '../../tokens';

import { BuilderModel } from './model';

export class ShareForm extends VDomRenderer<ShareForm.Model> {
  constructor(model: ShareForm.Model) {
    super(model);
    this.addClass(CSS.SHARE_FORM);
  }
  protected render(): JSX.Element {
    const { builderModel, icon, buttonLabel } = this.model;
    if (!builderModel.showShare || !builderModel.form) {
      this.hide();
      return <></>;
    }

    const { url } = this.model;

    this.show();
    return (
      <>
        <p>
          <label>
            Append this URL fragment to a JupyterLab URL to open
            <i> {builderModel.context.starter.label} </i>
            with the current body values.
          </label>
        </p>
        <div className={`${CSS.SHARE_FORM}-input`}>
          <label>
            <input
              type="checkbox"
              checked={this.model.withForm}
              onInput={this.onShowForm}
            ></input>
            Show Form?
          </label>
        </div>
        <div className={`${CSS.SHARE_FORM}-input`}>
          <input value={url} disabled />
          <button
            className={`${CSS.JP.styled} ${CSS.JP.accept}`}
            onClick={this.onClick}
            title="Copy to clipboard"
          >
            <icon.react tag="span" width={20} />
            <label>{buttonLabel}</label>
          </button>
        </div>
      </>
    );
  }

  onClick = (): void => this.model.copy();
  onShowForm = (): void => {
    this.model.withForm = !this.model.withForm;
  };
}

export namespace ShareForm {
  export class Model extends VDomModel {
    builderModel: BuilderModel;
    _icon: LabIcon = copyIcon;
    _withForm: boolean = true;

    constructor(builderModel: BuilderModel) {
      super();
      this.builderModel = builderModel;
      this.builderModel.stateChanged.connect(() => this.stateChanged.emit(void 0));
    }

    copy(): void {
      Clipboard.copyToSystem(this.url);
      this.icon = checkIcon;
      setTimeout(() => (this.icon = copyIcon), 500);
    }

    get url(): string {
      let rawParams: Record<string, any> = {
        [STARTER_NAME_PARAM]: this.builderModel.context.name,
        [STARTER_BODY_PARAM]: JSON.stringify(this.builderModel.form.formData),
      };

      if (!this._withForm) {
        rawParams = {
          ...rawParams,
          [STARTER_FORM_PARAM]: 0,
        };
      }

      const params = new URLSearchParams(rawParams);

      return `?${params.toString()}`;
    }

    get icon(): LabIcon {
      return this._icon;
    }

    set icon(icon: LabIcon) {
      this._icon = icon;
      this.stateChanged.emit(void 0);
    }

    get withForm(): boolean {
      return this._withForm;
    }

    set withForm(withForm: boolean) {
      this._withForm = withForm;
      this.stateChanged.emit(void 0);
    }

    get buttonLabel(): string {
      return this.icon === copyIcon ? 'Copy' : 'OK';
    }
  }
}
