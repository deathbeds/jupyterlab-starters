import { Widget } from '@phosphor/widgets';
import { JSONExt } from '@phosphor/coreutils';
import { PathExt, URLExt } from '@jupyterlab/coreutils';

import {
  ABCWidgetFactory,
  DocumentRegistry,
  DocumentWidget
} from '@jupyterlab/docregistry';

import { IDocumentManager } from '@jupyterlab/docmanager';

import { SchemaForm } from './schemaform';

// TODO: make configurable/detectable
export const INDENT = 2;

export class JSONSchemaFormDocument extends DocumentWidget<Widget> {
  content: SchemaForm;
  docManager: IDocumentManager;
  private _schemaModel: DocumentRegistry.IModel;
  private _schemaId: string;

  constructor(options: JSONSchemaFormDocument.IOptions) {
    super(options);
    this.docManager = options.docManager;

    const { context } = options;
    this.initToolbar();

    this.content.model.stateChanged.connect(this.onFormChange, this);

    context.ready
      .then(async () => await this.onContextReady())
      .catch(console.warn);
  }

  dispose() {
    if (this.isDisposed) {
      return;
    }
    this.content.model.stateChanged.disconnect(this.onFormChange, this);
    this.context.model.contentChanged.disconnect(this.onContentChanged, this);
    if (this.schemaModel) {
      this.schemaModel.contentChanged.disconnect(this.onSchema, this);
    }
    super.dispose();
  }

  /**
   * TODO:
   * - manual schema selection
   * - text formatting options: indent, sortkeys, etc
   */
  initToolbar() {
    //
  }

  async onFormChange() {
    this.context.model.fromString(
      JSON.stringify(this.content.model.formData, null, INDENT)
    );
  }

  async onContextReady() {
    this.context.model.contentChanged.connect(this.onContentChanged, this);
    await this.onContentChanged();
  }

  async onContentChanged() {
    let json: any;
    try {
      json = JSON.parse((this.context.model as any).value.text);
    } catch {
      return;
    }

    if (json) {
      const { $schema } = json;
      if ($schema) {
        this.schemaId = $schema;
      }

      if (!JSONExt.deepEqual(json, this.content.model.formData)) {
        this.content.model.formData = json;
      }
    }
  }

  get schemaId() {
    return this._schemaId;
  }

  set schemaId(schemaId) {
    if (this._schemaId === schemaId) {
      return;
    }

    this._schemaId = schemaId;

    if (this._schemaId) {
      if (this._schemaId.startsWith('.')) {
        // TODO: normalize?
        const path = PathExt.join(
          PathExt.dirname(this.context.path),
          this._schemaId
        );
        const widget = this.docManager.openOrReveal(path);
        if (widget) {
          this.schemaModel = widget.context.model;
        }
      } else {
        // handle explicit schema
        const uri = URLExt.parse(this._schemaId);
        console.error('TODO: handle uri', this._schemaId, uri);
      }
    }
  }

  get schemaModel() {
    return this._schemaModel;
  }

  set schemaModel(schemaModel) {
    if (this._schemaModel) {
      this._schemaModel.contentChanged.disconnect(this.onSchema, this);
    }
    this._schemaModel = schemaModel;
    if (this._schemaModel) {
      this._schemaModel.contentChanged.connect(this.onSchema, this);
    }
  }

  async onSchema() {
    if (this._schemaModel != null) {
      let json: any;
      try {
        json = JSON.parse((this._schemaModel as any).value.text);
      } catch (err) {
        console.warn(err);
      }
      if (json && !JSONExt.deepEqual(this.content.model.schema, json)) {
        this.content.model.schema = json;
      }
    }
  }
}

export namespace JSONSchemaFormDocument {
  export interface IOptions extends DocumentWidget.IOptions<SchemaForm> {
    docManager: IDocumentManager;
  }
}

/**
 * A widget factory for rjsf.
 */
export class JSONSchemaFormFactory extends ABCWidgetFactory<
  JSONSchemaFormDocument,
  DocumentRegistry.IModel
> {
  private docManager: IDocumentManager;

  /**
   * Create a new widget given a context.
   */
  constructor(options: JSONSchemaFormFactory.IOptions) {
    super(options);
    this.docManager = options.docManager;
  }

  protected createNewWidget(
    context: DocumentRegistry.Context
  ): JSONSchemaFormDocument {
    return new JSONSchemaFormDocument({
      context,
      docManager: this.docManager,
      content: new SchemaForm({})
    });
  }
}

export namespace JSONSchemaFormFactory {
  export interface IOptions extends DocumentRegistry.IWidgetFactoryOptions {
    docManager: IDocumentManager;
  }
}
