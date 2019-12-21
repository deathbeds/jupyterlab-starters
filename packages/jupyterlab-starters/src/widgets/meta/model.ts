import { JSONObject, JSONExt } from '@phosphor/coreutils';
import { CommandRegistry } from '@phosphor/commands';
import { Widget } from '@phosphor/widgets';
import { VDomModel } from '@jupyterlab/apputils';

import { NotebookPanel } from '@jupyterlab/notebook';

// @ts-ignore
import * as SCHEMA_DEFAULT from '../../_schema.json';

import { IStarterManager } from '../../tokens';

import { SchemaFormModel } from '../schemaform/model';

const RAW_SCHEMA = (SCHEMA_DEFAULT as any).default;
const NOTEBOOK_META_KEY = 'jupyter_starters';
const NOTEBOOK_META_SUBKEY = 'starter';

export class NotebookMetadataModel extends VDomModel {
  private _form: SchemaFormModel<JSONObject>;
  private _notebook: NotebookPanel;
  // private _manager: IStarterManager;
  private _commands: CommandRegistry;

  constructor(options: NotebookMetadataModel.IOptions) {
    super();
    // this._manager = options.manager;
    this._commands = options.commands;
  }

  get liveSchema() {
    const { definitions } = RAW_SCHEMA;

    let commandIds = this._commands.listCommands().filter(id => {
      return (id || '').trim().length;
    });
    commandIds.sort();
    definitions.command.properties.id.enum = commandIds;

    const starterMeta = definitions['starter-meta'];

    let schema = {
      definitions,
      type: 'object',
      ...starterMeta
    };

    delete schema['required'];

    return schema;
  }

  get notebook() {
    return this._notebook;
  }

  set notebook(notebook) {
    if (this._notebook) {
      this._notebook.model.metadata.changed.disconnect(
        this.onNotebookMeta,
        this
      );
    }

    this._notebook = notebook;

    if (this._notebook) {
      this._notebook.model.metadata.changed.connect(this.onNotebookMeta, this);
      this.onNotebookMeta();
    }
    this.stateChanged.emit(void 0);
  }

  onNotebookMeta() {
    const fromNotebook = this._notebook.model.metadata.get(
      NOTEBOOK_META_KEY
    ) as JSONObject;
    if (fromNotebook && fromNotebook[NOTEBOOK_META_SUBKEY]) {
      const candidate = fromNotebook[NOTEBOOK_META_SUBKEY] as JSONObject;
      if (!JSONExt.deepEqual(this._form.formData, candidate)) {
        this._form.formData = candidate;
      }
    }
  }

  get form() {
    return this._form;
  }

  set form(form) {
    if (this._form) {
      this._form.stateChanged.disconnect(this._change, this);
    }
    this._form = form;
    form.stateChanged.connect(this._change, this);
    this._change();
  }

  private _change = () => {
    const { formData } = this._form;
    if (this._notebook && formData) {
      const fromNotebook =
        this._notebook.model.metadata.get(NOTEBOOK_META_KEY) || ({} as any);
      const nbStarter = fromNotebook[NOTEBOOK_META_SUBKEY] || {};
      let candidate = {
        ...fromNotebook,
        [NOTEBOOK_META_SUBKEY]: {
          ...nbStarter,
          ...formData
        }
      };

      if (!JSONExt.deepEqual(fromNotebook, candidate)) {
        this._notebook.model.metadata.set(NOTEBOOK_META_KEY, candidate);
      }
    }
    this.stateChanged.emit(void 0);
  };
}

export namespace NotebookMetadataModel {
  export interface IOptions extends Widget.IOptions {
    manager: IStarterManager;
    commands: CommandRegistry;
  }
}