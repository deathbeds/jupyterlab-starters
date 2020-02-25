import { Widget } from '@phosphor/widgets';
import { JSONExt } from '@phosphor/coreutils';
import { IIterator } from '@phosphor/algorithm';
import { PathExt, URLExt } from '@jupyterlab/coreutils';

import {
  ABCWidgetFactory,
  DocumentRegistry,
  DocumentWidget
} from '@jupyterlab/docregistry';

import { Toolbar } from '@jupyterlab/apputils';

import { IDocumentManager } from '@jupyterlab/docmanager';

import { SchemaForm } from '../schemaform';

import { SchemaFinder, Indenter } from './toolbar';

// TODO: make configurable/detectable
export const INDENT = 2;
export const DOC_CLASS = 'jp-SchemaForm-Document';

export class JSONSchemaFormDocument extends DocumentWidget<Widget> {
  content: SchemaForm;
  docManager: IDocumentManager;
  getOpenWidgets: () => IIterator<Widget>;
  private _schemaModel: DocumentRegistry.IModel;
  private _schemaId: string;
  private _schemaFinder: SchemaFinder;
  private _indenter: Indenter;

  constructor(options: JSONSchemaFormDocument.IOptions) {
    super(options);
    this.addClass(DOC_CLASS);
    this.docManager = options.docManager;
    this.getOpenWidgets = options.getOpenWidgets;

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
    this._schemaFinder = new SchemaFinder();
    this._schemaFinder.model.getOpenWidgets = this.getOpenWidgets;
    this._schemaFinder.model.stateChanged.connect(this.onSchemaFound, this);

    this._indenter = new Indenter();
    this.toolbar.addItem('schema', this._schemaFinder);
    this.toolbar.addItem('spacer', Toolbar.createSpacerItem());
    this.toolbar.addItem('indenter', this._indenter);

    this._indenter.model.stateChanged.connect(this.onFormChange, this);
  }

  async onFormChange() {
    this.context.model.fromString(
      JSON.stringify(
        this.content.model.formData,
        null,
        this._indenter.model.indent
      )
    );
  }

  async onSchemaFound() {
    const model = this._schemaFinder.model.schemaContext?.model;
    if (
      model != null &&
      model !== this.schemaModel &&
      model !== this.context.model
    ) {
      this._schemaId = null;
      this.schemaModel = model;
    }
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
      if ($schema && !this._schemaFinder.model.schemaPath) {
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
      this.onSchema().catch(console.warn);
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
    getOpenWidgets: () => IIterator<Widget>;
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
  private getOpenWidgets: () => IIterator<Widget>;

  /**
   * Create a new widget given a context.
   */
  constructor(options: JSONSchemaFormFactory.IOptions) {
    super(options);
    this.docManager = options.docManager;
    this.getOpenWidgets = options.getOpenWidgets;
  }

  protected createNewWidget(
    context: DocumentRegistry.Context
  ): JSONSchemaFormDocument {
    return new JSONSchemaFormDocument({
      context,
      docManager: this.docManager,
      getOpenWidgets: this.getOpenWidgets,
      content: new SchemaForm({})
    });
  }
}

export namespace JSONSchemaFormFactory {
  export interface IOptions extends DocumentRegistry.IWidgetFactoryOptions {
    docManager: IDocumentManager;
    getOpenWidgets: () => IIterator<Widget>;
  }
}
