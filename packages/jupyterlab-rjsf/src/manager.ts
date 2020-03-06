import { toArray } from '@lumino/algorithm';
import { Signal } from '@lumino/signaling';
import { JSONObject } from '@lumino/coreutils';

import { Widget } from '@lumino/widgets';
import { ILabShell } from '@jupyterlab/application';
import { ISchemaManager } from './tokens';
import { IRenderMimeRegistry, RenderedMarkdown } from '@jupyterlab/rendermime';

import { DocumentRegistry } from '@jupyterlab/docregistry';

type IReaderFull = ISchemaManager.IContextMatcher & ISchemaManager.IReader;
type IWriterFull = ISchemaManager.IContextMatcher & ISchemaManager.IWriter;

export class SchemaManager implements ISchemaManager {
  private _widgetsChanged: Signal<ISchemaManager, void>;
  private _rendermime: IRenderMimeRegistry;
  private _shell: ILabShell;
  private _widgets: Widget[] = [];
  private _markdown: RenderedMarkdown;
  private _readers: IReaderFull[] = [];
  private _writers: IWriterFull[] = [];

  constructor(options: SchemaManager.IOptions) {
    this._shell = options.shell;
    this._rendermime = options.rendermime;
    this._widgetsChanged = new Signal<ISchemaManager, void>(this);
    this._shell.layoutModified.connect(this.onLayoutModified, this);
  }

  isActive(widget: Widget) {
    return this._shell.activeWidget === widget;
  }

  registerReader(reader: IReaderFull) {
    this._readers.push(reader);
  }

  registerWriter(writer: IWriterFull) {
    this._writers.push(writer);
  }

  handles(action: string, context: DocumentRegistry.Context) {
    return true;
  }

  async read(context: DocumentRegistry.Context) {
    for (const reader of this._readers) {
      if (reader.handles('read', context)) {
        return await reader.read(context);
      }
    }
  }

  async write(value: JSONObject, context: DocumentRegistry.Context) {
    for (const writer of this._writers) {
      if (writer.handles('write', context)) {
        return await writer.write(value, context);
      }
    }
  }

  get widgetsChanged() {
    return this._widgetsChanged;
  }

  get markdown() {
    if (!this._markdown) {
      this._markdown = this._rendermime.createRenderer(
        'text/markdown'
      ) as RenderedMarkdown;
    }
    return this._markdown;
  }

  protected onLayoutModified() {
    const widgets = toArray(this._shell.widgets());
    let changed = widgets.length !== this._widgets.length;

    for (const widget of widgets) {
      if (changed) {
        break;
      }
      if (this._widgets.indexOf(widget) === -1) {
        changed = true;
      }
    }

    if (changed) {
      this._widgets = widgets;
      this._widgetsChanged.emit(void 0);
    }
  }

  get widgets() {
    return this._widgets;
  }
}

export namespace SchemaManager {
  export interface IOptions {
    shell: ILabShell;
    rendermime: IRenderMimeRegistry;
  }
}
