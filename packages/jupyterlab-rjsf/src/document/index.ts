import { Widget } from '@phosphor/widgets';
import { JSONExt, JSONObject } from '@phosphor/coreutils';
import { PathExt, URLExt } from '@jupyterlab/coreutils';
import { ALL_CUSTOM_UI } from '../fields';

import {
  ABCWidgetFactory,
  DocumentRegistry,
  DocumentWidget
} from '@jupyterlab/docregistry';

import { Toolbar } from '@jupyterlab/apputils';

import { IDocumentManager } from '@jupyterlab/docmanager';

import { SchemaForm } from '../schemaform';

import { SchemaFinder, Indenter, Toggle } from './toolbar';
import { ISchemaManager } from '../tokens';

export const DOC_CLASS = 'jp-SchemaForm-Document';

export class JSONSchemaFormDocument extends DocumentWidget<Widget> {
  content: SchemaForm;
  docManager: IDocumentManager;
  schemaManager: ISchemaManager;
  private _schemaContext: DocumentRegistry.Context;
  private _uiSchemaContext: DocumentRegistry.Context;
  private _schemaId: string;
  private _schemaFinder: SchemaFinder;
  private _uiSchemaFinder: SchemaFinder;
  private _indenter: Indenter;
  private _liveValidate: Toggle;
  private _liveOmit: Toggle;
  private _liveMarkdown: Toggle;

  constructor(options: JSONSchemaFormDocument.IOptions) {
    super(options);
    this.addClass(DOC_CLASS);
    this.docManager = options.docManager;
    this.schemaManager = options.schemaManager;

    const { context } = options;
    this.initToolbar();

    this.content.model.stateChanged.connect(this.onFormChange, this);

    context.ready.then(async () => this.onContextReady()).catch(console.warn);

    this.onPathChanged();
  }

  dispose() {
    if (this.isDisposed) {
      return;
    }
    this.content.model.stateChanged.disconnect(this.onFormChange, this);
    this.context.model.contentChanged.disconnect(this.onContentChanged, this);
    if (this.schemaContext) {
      this.schemaContext.model.contentChanged.disconnect(this.onSchema, this);
    }
    this._liveValidate.model.stateChanged.disconnect(
      this.onValidationChanged,
      this
    );
    this._liveOmit.model.stateChanged.disconnect(this.onOmitChanged, this);
    this._liveMarkdown.model.stateChanged.disconnect(
      this.onMarkdownChanged,
      this
    );
    this._schemaFinder.dispose();
    this._uiSchemaFinder.dispose();
    this._indenter.dispose();
    super.dispose();
  }

  /**
   * TODO:
   * - manual schema selection
   * - text formatting options: indent, sortkeys, etc
   */
  initToolbar() {
    this._schemaFinder = new SchemaFinder({
      showDetect: 'from $schema',
      canary: 'properties'
    });
    this._schemaFinder.model.label = 'JSON';
    this._schemaFinder.model.schemaManager = this.schemaManager;
    this._schemaFinder.model.stateChanged.connect(this.onSchemaFound, this);

    this._uiSchemaFinder = new SchemaFinder({
      showDetect: '-',
      canary: 'ui:'
    });
    this._uiSchemaFinder.model.label = 'UI';
    this._uiSchemaFinder.model.schemaManager = this.schemaManager;
    this._uiSchemaFinder.model.stateChanged.connect(this.onUiSchemaFound, this);

    this._indenter = new Indenter();
    this._indenter.model.stateChanged.connect(this.onFormChange, this);

    this._liveValidate = new Toggle({
      label: 'Validate',
      value: this.content.model.props.liveValidate
    });
    this._liveValidate.model.stateChanged.connect(
      this.onValidationChanged,
      this
    );

    this._liveOmit = new Toggle({
      label: 'Omit',
      value: this.content.model.props.liveOmit
    });
    this._liveOmit.model.stateChanged.connect(this.onOmitChanged, this);

    this._liveMarkdown = new Toggle({
      label: 'Markdown',
      value: this.content.model.liveMarkdown
    });
    this._liveMarkdown.model.stateChanged.connect(this.onMarkdownChanged, this);

    this.toolbar.addItem('schema', this._schemaFinder);
    this.toolbar.addItem('ui', this._uiSchemaFinder);
    this.toolbar.addItem('spacer1', Toolbar.createSpacerItem());
    this.toolbar.addItem('markdown', this._liveMarkdown);
    this.toolbar.addItem('validation', this._liveValidate);
    this.toolbar.addItem('omit', this._liveOmit);
    this.toolbar.addItem('spacer2', Toolbar.createSpacerItem());
    this.toolbar.addItem('indenter', this._indenter);
  }

  async onFormChange() {
    if (!this.schemaManager.isActive(this)) {
      return;
    }
    await this.schemaManager.write(
      this.content.model.formData as JSONObject,
      this.context
    );
  }

  onSchemaFound() {
    const context = this._schemaFinder.model.schemaContext;
    if (
      context != null &&
      context !== this.schemaContext &&
      context !== this.context
    ) {
      this._schemaId = null;
      this.schemaContext = context;
    }
  }

  onUiSchemaFound() {
    const context = this._uiSchemaFinder.model.schemaContext;
    if (
      context != null &&
      context !== this.uiSchemaContext &&
      context !== this.context
    ) {
      this.uiSchemaContext = context;
    }
  }

  onContextReady() {
    this.context.model.contentChanged.connect(this.onContentChanged, this);
    this.context.pathChanged.connect(this.onPathChanged, this);
    this.onContentChanged().catch(console.warn);
    this.onPathChanged();
  }

  async onContentChanged() {
    if (this.schemaManager.isActive(this)) {
      return;
    }

    let json: any;

    try {
      json = await this.schemaManager.read(this.context);
    } catch {
      return;
    }

    if (json) {
      const { $schema } = json;
      if ($schema && !this._schemaFinder.model.schemaPath) {
        this.schemaId = $schema;
      }

      if (JSONExt.deepEqual(json, this.content.model.formData)) {
        return;
      }

      this.content.model.formData = json;
    }
  }

  onPathChanged() {
    this._schemaFinder.model.basePath = this.context.path;
    this._uiSchemaFinder.model.basePath = this.context.path;
  }

  onValidationChanged() {
    const { model } = this.content;
    model.props = {
      ...model.props,
      liveValidate: this._liveValidate.model.value
    };
  }

  onMarkdownChanged() {
    const { model } = this.content;
    model.liveMarkdown = this._liveMarkdown.model.value;
  }

  onOmitChanged() {
    const { model } = this.content;
    model.props = {
      ...model.props,
      liveOmit: this._liveOmit.model.value
    };
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
        const widget = this.docManager.openOrReveal(path, 'Editor', null, {
          mode: 'split-right'
        });
        if (widget) {
          this.schemaContext = widget.context;
        }
      } else {
        // handle explicit schema
        const uri = URLExt.parse(this._schemaId);
        console.error('TODO: handle uri', this._schemaId, uri);
      }
    }
  }

  get schemaContext() {
    return this._schemaContext;
  }

  set schemaContext(schemaModel) {
    if (this._schemaContext) {
      this._schemaContext.model.contentChanged.disconnect(this.onSchema, this);
    }
    this._schemaContext = schemaModel;
    if (this._schemaContext) {
      this._schemaContext.model.contentChanged.connect(this.onSchema, this);
      this.onSchema().catch(console.warn);
    }
  }

  get uiSchemaContext() {
    return this._schemaContext;
  }

  set uiSchemaContext(uiSchemaContext) {
    if (this._uiSchemaContext) {
      this._uiSchemaContext.model.contentChanged.disconnect(
        this.onUiSchema,
        this
      );
    }
    this._uiSchemaContext = uiSchemaContext;
    if (this._uiSchemaContext) {
      this._uiSchemaContext.model.contentChanged.connect(this.onUiSchema, this);
      this.onUiSchema().catch(console.warn);
    }
  }

  async onSchema() {
    if (this._schemaContext != null) {
      let json: JSONObject;
      let text: string;
      try {
        json = await this.schemaManager.read(this._schemaContext);
      } catch (err) {
        console.warn(err, text);
      }
      if (
        json &&
        this.content.model.schema &&
        JSONExt.deepEqual(this.content.model.schema, json)
      ) {
        return;
      }

      if (json) {
        this.content.model.schema = json;
        this.content.model.stateChanged.emit(void 0);
      }
    }
  }

  async onUiSchema() {
    if (this._uiSchemaContext != null) {
      let json: JSONObject;
      let text: string;
      try {
        json = await this.schemaManager.read(this._uiSchemaContext);
      } catch (err) {
        console.warn(err, text);
      }
      if (
        json &&
        this.content.model.uiSchema &&
        JSONExt.deepEqual(this.content.model.uiSchema, json)
      ) {
        return;
      }

      if (json) {
        this.content.model.uiSchema = json;
        this.content.model.stateChanged.emit(void 0);
      }
    }
  }
}

export namespace JSONSchemaFormDocument {
  export interface IOptions extends DocumentWidget.IOptions<SchemaForm> {
    docManager: IDocumentManager;
    schemaManager: ISchemaManager;
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
  private schemaManager: ISchemaManager;

  /**
   * Create a new widget given a context.
   */
  constructor(options: JSONSchemaFormFactory.IOptions) {
    super(options);
    this.docManager = options.docManager;
    this.schemaManager = options.schemaManager;
  }

  protected createNewWidget(
    context: DocumentRegistry.Context
  ): JSONSchemaFormDocument {
    const { docManager, schemaManager } = this;
    const { markdown } = schemaManager;

    const content = new SchemaForm(
      {},
      {
        liveValidate: true,
        ...ALL_CUSTOM_UI
      },
      { markdown, liveMarkdown: true }
    );

    return new JSONSchemaFormDocument({
      context,
      docManager,
      schemaManager,
      content
    });
  }
}

export namespace JSONSchemaFormFactory {
  export interface IOptions extends DocumentRegistry.IWidgetFactoryOptions {
    docManager: IDocumentManager;
    schemaManager: ISchemaManager;
  }
}
