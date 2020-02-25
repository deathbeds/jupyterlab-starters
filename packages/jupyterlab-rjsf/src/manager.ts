import { toArray } from '@phosphor/algorithm';
import { Signal } from '@phosphor/signaling';
import { Widget } from '@phosphor/widgets';
import { ILabShell } from '@jupyterlab/application';
import { ISchemaManager } from './tokens';
import { IRenderMimeRegistry, RenderedMarkdown } from '@jupyterlab/rendermime';

export class SchemaManager implements ISchemaManager {
  private _widgetsChanged: Signal<ISchemaManager, void>;
  private _rendermime: IRenderMimeRegistry;
  private _shell: ILabShell;
  private _widgets: Widget[] = [];
  private _markdown: RenderedMarkdown;

  constructor(options: SchemaManager.IOptions) {
    this._shell = options.shell;
    this._rendermime = options.rendermime;
    this._widgetsChanged = new Signal<ISchemaManager, void>(this);
    this._shell.layoutModified.connect(this.onLayoutModified, this);
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
      this.widgetsChanged.emit(void 0);
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
