import { JSONObject } from '@lumino/coreutils';
import { Widget, BoxLayout } from '@lumino/widgets';

import { IStartContext } from '../../tokens';
import { CSS } from '../../css';

import { SchemaForm } from '@deathbeds/jupyterlab-rjsf';

import { BuilderModel } from './model';
import { BuilderButtons } from './buttons';
import { ALL_CUSTOM_UI } from '@deathbeds/jupyterlab-rjsf';

export class BodyBuilder extends Widget {
  private _form: SchemaForm<JSONObject>;
  private _context: IStartContext;
  private _buttons: BuilderButtons;

  model: BuilderModel;

  constructor(options: BuilderModel.IOptions) {
    super(options);
    this.model = new BuilderModel(options);
    this.model.done = () => this.dispose();
    this.layout = new BoxLayout();
    this._context = options.context;
    const { label } = this._context.starter;
    this.id = Private.nextId();
    this.addClass(CSS.BUILDER);
    this.addClass(CSS.FORM_PANEL);
    this.title.caption = label;
    if (this.model.icon) {
      this.title.icon = this.model.icon;
    }
    this.initForm().catch(console.warn);
  }

  protected async initForm() {
    this._form = new SchemaForm(
      this._context.starter.schema || {},
      {
        liveValidate: true,
        formData: this._context.body,
        uiSchema: this._context.starter.uiSchema || {},
        ...(await ALL_CUSTOM_UI()),
      },
      { markdown: this.model.manager.markdown }
    );

    this._buttons = this.makeButtons();
    this.boxLayout.addWidget(this._form);
    this.boxLayout.addWidget(this._buttons);
  }

  get boxLayout() {
    return this.layout as BoxLayout;
  }

  dispose() {
    super.dispose();
    if (!this.isDisposed) {
      this.model.dispose();
    }
  }

  makeButtons() {
    const buttons = new BuilderButtons(this.model);

    buttons.model.form = this._form.model;

    return buttons;
  }
}

namespace Private {
  let _nextId = 0;
  export function nextId() {
    return `id-jp-starters-${name}-${_nextId++}`;
  }
}
