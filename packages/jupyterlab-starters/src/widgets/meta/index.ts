import {
  SchemaForm,
  ALL_CUSTOM_UI,
  AS_JSONOBJECT,
  AS_TEXTAREA,
  AS_XML,
} from '@deathbeds/jupyterlab-rjsf';
import { JSONObject } from '@lumino/coreutils';
import { Widget, BoxLayout } from '@lumino/widgets';

import { CSS } from '../../css';
import { PreviewCard } from '../previewcard';

import { NotebookMetadataModel } from './model';

export class NotebookMetadata extends Widget {
  private _form: SchemaForm<JSONObject>;
  private _preview: PreviewCard;

  model: NotebookMetadataModel;

  constructor(options: NotebookMetadataModel.IOptions) {
    super(options);
    this.model = new NotebookMetadataModel(options);
    this.layout = new BoxLayout();
    this.id = Private.nextId();
    this.addClass(CSS.META);
    this.addClass(CSS.FORM_PANEL);
    this.initForm().catch(console.error);
  }

  protected async initForm(): Promise<void> {
    this._form = new SchemaForm(
      this.model.liveSchema,
      {
        liveValidate: true,
        uiSchema: {
          description: AS_TEXTAREA,
          icon: AS_XML,
          schema: AS_JSONOBJECT,
          uiSchema: AS_JSONOBJECT,
          commands: {
            items: {
              args: AS_JSONOBJECT,
            },
          },
        },
        ...(await ALL_CUSTOM_UI()),
      },
      { markdown: this.model.manager.markdown }
    );
    this.model.form = this._form.model;

    this._preview = new PreviewCard();
    this.model.stateChanged.connect(() => {
      this._preview.model.starter = (this.model.form.formData as any) || {};
      this._form.setHidden(!this.model.notebook);
    });

    this.boxLayout.addWidget(this._form);
    this.boxLayout.addWidget(this._preview);
  }

  get boxLayout(): BoxLayout {
    return this.layout as BoxLayout;
  }

  dispose(): void {
    super.dispose();
    if (!this.isDisposed) {
      this.model.dispose();
    }
  }
}

namespace Private {
  let _nextId = 0;
  export function nextId(): string {
    return `id-jp-starters-notebook-${_nextId++}`;
  }
}
