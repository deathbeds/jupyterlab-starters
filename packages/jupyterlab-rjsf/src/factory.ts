import { Widget } from '@phosphor/widgets';

import {
  ABCWidgetFactory,
  DocumentRegistry,
  DocumentWidget
} from '@jupyterlab/docregistry';

import {IDocumentManager} from '@jupyterlab/docmanager';

import { SchemaForm } from './schemaform';

export class JSONSchemaFormDocument extends DocumentWidget<Widget> {
  content: SchemaForm;
  docManager: IDocumentManager;
  schemaWidget: DocumentWidget;

  constructor(options: JSONSchemaFormDocument.IOptions) {
    super(options);
    this.docManager = options.docManager;

    const { context } = options;
    this.initToolbar();

    this.content.model.stateChanged.connect(() => {
      this.context.model.fromJSON(this.content.model.formData);
    });

    context.ready
      .then(async () => {
        context.model.contentChanged.connect(this.onContentChanged, this);
        await this.onContentChanged();
      })
      .catch(console.warn);
  }

  initToolbar() {
    // TODO
  }

  async onContentChanged() {
    let json: any;
    try {
      json = JSON.parse((this.context.model as any).value.text);
    } catch {
      return;
    }

    if(json) {
      const {$schema} = json;
      if ($schema) {
        this.schemaWidget = this.docManager.open($schema) as any;
        console.log(this.schemaWidget);
        const schemaText = (this.schemaWidget.context.model as any).value.text;
        try {
          this.content.model.schema = JSON.parse(schemaText);
        } catch(err) {
          console.error(err);
        }
      }
      this.content.model.formData = json;
    }
  }
}

export namespace JSONSchemaFormDocument {
  export interface IOptions extends DocumentWidget.IOptions<SchemaForm>{
    docManager: IDocumentManager
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
