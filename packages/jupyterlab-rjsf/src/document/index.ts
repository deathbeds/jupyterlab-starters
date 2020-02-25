import { Widget } from '@phosphor/widgets';
import { JSONExt } from '@phosphor/coreutils';
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
  private _schemaModel: DocumentRegistry.IModel;
  private _uiSchemaModel: DocumentRegistry.IModel;
  private _schemaId: string;
  private _schemaFinder: SchemaFinder;
  private _uiSchemaFinder: SchemaFinder;
  private _indenter: Indenter;
  private _liveValidation: Toggle;
  private _liveOmit: Toggle;

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
    if (this.schemaModel) {
      this.schemaModel.contentChanged.disconnect(this.onSchema, this);
    }
    this._liveValidation.model.stateChanged.disconnect(
      this.onValidationChanged,
      this
    );
    this._liveOmit.model.stateChanged.disconnect(this.onOmitChanged, this);
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

    this._liveValidation = new Toggle({ label: 'Validate', value: true });
    this._liveValidation.model.stateChanged.connect(
      this.onValidationChanged,
      this
    );

    this._liveOmit = new Toggle({ label: 'Omit', value: false });
    this._liveOmit.model.stateChanged.connect(this.onOmitChanged, this);

    this.toolbar.addItem('schema', this._schemaFinder);
    this.toolbar.addItem('ui', this._uiSchemaFinder);
    this.toolbar.addItem('spacer1', Toolbar.createSpacerItem());
    this.toolbar.addItem('validation', this._liveValidation);
    this.toolbar.addItem('omit', this._liveOmit);
    this.toolbar.addItem('spacer2', Toolbar.createSpacerItem());
    this.toolbar.addItem('indenter', this._indenter);
  }

  onFormChange() {
    this.context.model.fromString(
      JSON.stringify(
        this.content.model.formData,
        null,
        this._indenter.model.indent
      ) + '\n'
    );
  }

  onSchemaFound() {
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

  onUiSchemaFound() {
    const model = this._uiSchemaFinder.model.schemaContext?.model;
    if (
      model != null &&
      model !== this.uiSchemaModel &&
      model !== this.context.model
    ) {
      this.uiSchemaModel = model;
    }
  }

  onContextReady() {
    this.context.model.contentChanged.connect(this.onContentChanged, this);
    this.context.pathChanged.connect(this.onPathChanged, this);
    this.onContentChanged();
    this.onPathChanged();
  }

  onContentChanged() {
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

      if (JSONExt.deepEqual(json, this.content.model.formData)) {
        return;
      }

      this.content.model.formData = json || {};
    }
  }

  onPathChanged() {
    this._schemaFinder.model.basePath = this.context.path;
    this._uiSchemaFinder.model.basePath = this.context.path;
  }

  onValidationChanged() {
    this.content.model.props.liveValidate = this._liveValidation.model.value;
    this.content.model.stateChanged.emit(void 0);
  }

  onOmitChanged() {
    this.content.model.props.liveOmit = this._liveOmit.model.value;
    this.content.model.stateChanged.emit(void 0);
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
      this.onSchema();
    }
  }

  get uiSchemaModel() {
    return this._schemaModel;
  }

  set uiSchemaModel(uiSchemaModel) {
    if (this._uiSchemaModel) {
      this._uiSchemaModel.contentChanged.disconnect(this.onUiSchema, this);
    }
    this._uiSchemaModel = uiSchemaModel;
    if (this._uiSchemaModel) {
      this._uiSchemaModel.contentChanged.connect(this.onUiSchema, this);
      this.onUiSchema();
    }
  }

  onSchema() {
    if (this._schemaModel != null) {
      let json = {};
      let text: string;
      try {
        text = (this._schemaModel as any).value.text;
        json = JSON.parse(text);
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

      this.content.model.schema = json || {};
      this.content.model.stateChanged.emit(void 0);
    }
  }

  onUiSchema() {
    if (this._uiSchemaModel != null) {
      let json = {};
      let text: string;
      try {
        text = (this._uiSchemaModel as any).value.text;
        json = JSON.parse(text);
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

      this.content.model.uiSchema = json || {};
      this.content.model.stateChanged.emit(void 0);
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
      { markdown }
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
