import React from 'react';
import { PathExt } from '@jupyterlab/coreutils';
import { HTMLSelect } from '@jupyterlab/ui-components';
import { VDomRenderer, VDomModel } from '@jupyterlab/apputils';
import { DocumentRegistry, DocumentWidget } from '@jupyterlab/docregistry';
import { ISchemaManager } from '../tokens';

const CARET = {
  icon: <span className="jp-MaterialIcon jp-DownCaretIcon bp3-icon" />
};

export class SchemaFinder extends VDomRenderer<SchemaFinder.Model> {
  constructor(options: SchemaFinder.IOptions) {
    super();
    this.model = new SchemaFinder.Model(options);
  }

  dispose() {
    if (this.isDisposed) {
      return;
    }
    this.model.dispose();
    super.dispose();
  }

  protected render() {
    const label = this.model.label;
    const base = this.model.basePath
      ? PathExt.dirname(this.model.basePath)
      : null;
    return (
      <label>
        <span>{label}</span>
        <HTMLSelect
          aria-label={label}
          minimal
          iconProps={CARET}
          value={this.model.schemaPath}
          onChange={this.handleChange}
        >
          <option value="">{this.model.showDetect || '-'}</option>
          <optgroup label={`Open ${label}`}>
            {this.model.jsonContexts.map((ctx, i) => {
              return (
                <option key={ctx.path} value={ctx.path}>
                  {base ? PathExt.relative(base, ctx.path) : ctx.path}
                </option>
              );
            })}
          </optgroup>
          <option value="refresh">Refresh</option>
        </HTMLSelect>
      </label>
    );
  }

  handleChange = (event: React.ChangeEvent<HTMLSelectElement>): void => {
    const path = event.currentTarget.value;
    if (!path) {
      this.model.schemaContext = null;
    }

    if (path === 'refresh') {
      this.model.onWidgetsChanged();
      return;
    }

    const contexts = this.model.jsonContexts.filter(ctx => {
      return ctx.path === path;
    });

    if (contexts.length) {
      this.model.schemaContext = contexts[0];
    } else {
      this.model.schemaContext = null;
    }
  };
}

export namespace SchemaFinder {
  export interface IOptions {
    showDetect: string;
    canary: string;
  }
  export class Model extends VDomModel {
    private _schemaManager: ISchemaManager;
    private _schemaContext: DocumentRegistry.IContext<DocumentRegistry.IModel>;
    private _contexts: DocumentRegistry.IContext<DocumentRegistry.IModel>[];
    private _label: string;
    private _basePath: string;
    private _showDetect: string;
    private _canary: string;

    constructor(options: IOptions) {
      super();
      this._showDetect = options.showDetect;
      this._canary = options.canary;
    }

    dispose() {
      if (this.isDisposed) {
        return;
      }
      this._schemaManager.widgetsChanged.disconnect(
        this.onWidgetsChanged,
        this
      );
      this._schemaManager = null;
      super.dispose();
    }

    onWidgetsChanged() {
      const contexts = new Map<
        string,
        DocumentRegistry.IContext<DocumentRegistry.IModel>
      >();
      if (this._schemaManager != null) {
        const widgets = this._schemaManager.widgets;
        for (const widget of widgets) {
          if (widget instanceof DocumentWidget) {
            const { context } = widget;
            if (context.path === this._basePath) {
              continue;
            }
            if (context.model.value.text.indexOf(this._canary) !== -1) {
              contexts.set(context.path, context);
            }
          }
        }
      }
      this._contexts = Array.from(contexts.values());

      this.stateChanged.emit(void 0);
    }

    get showDetect() {
      return this._showDetect;
    }

    get canary() {
      return this._canary;
    }

    set canary(canary) {
      this._canary = canary;
      this.stateChanged.emit(void 0);
    }

    get basePath() {
      return this._basePath;
    }

    set basePath(basePath) {
      if (this._basePath !== basePath) {
        this._basePath = basePath;
        this.stateChanged.emit(void 0);
      }
    }

    get label() {
      return this._label;
    }

    set label(label) {
      if (this._label !== label) {
        this._label = label;
        this.stateChanged.emit(void 0);
      }
    }

    set schemaManager(schemaManager: ISchemaManager) {
      if (this._schemaManager) {
        this._schemaManager.widgetsChanged.disconnect(
          this.onWidgetsChanged,
          this
        );
      }
      this._schemaManager = schemaManager;
      if (this._schemaManager) {
        this._schemaManager.widgetsChanged.connect(this.onWidgetsChanged, this);
      }
      this.stateChanged.emit(void 0);
    }

    get schemaPath() {
      return this._schemaContext?.path || '';
    }

    get schemaContext() {
      return this._schemaContext;
    }

    set schemaContext(schemaContext) {
      this._schemaContext = schemaContext;
      this.stateChanged.emit(void 0);
    }

    get jsonContexts() {
      return this._contexts || [];
    }
  }
}

export class Indenter extends VDomRenderer<Indenter.Model> {
  constructor() {
    super();
    this.model = new Indenter.Model();
  }

  dispose() {
    if (this.isDisposed) {
      return;
    }
    this.model.dispose();
    super.dispose();
  }

  protected render() {
    return (
      <label>
        <span>Indent</span>
        <HTMLSelect
          aria-label="Indent Count"
          minimal
          iconProps={CARET}
          onChange={this.handleCount}
          value={this.model.count}
        >
          {Array.from(Array(11).keys()).map(i => (
            <option key={i} value={i}>
              {i}
            </option>
          ))}
        </HTMLSelect>
        <HTMLSelect
          aria-label="Indent Character"
          minimal
          iconProps={CARET}
          onChange={this.handleCharacter}
          value={this.model.character}
        >
          <option value=" ">spaces</option>
          <option value={'\t'}>tabs</option>
        </HTMLSelect>
      </label>
    );
  }

  handleCharacter = (event: React.ChangeEvent<HTMLSelectElement>): void => {
    this.model.character = event.currentTarget.value;
  };

  handleCount = (event: React.ChangeEvent<HTMLSelectElement>): void => {
    this.model.count = parseInt(event.currentTarget.value, 10);
  };
}

export namespace Indenter {
  export class Model extends VDomModel {
    private _character = ' ';
    private _count = 2;
    get character() {
      return this._character;
    }
    set character(character) {
      if (this._character !== character) {
        this._character = character;
        this.stateChanged.emit(void 0);
      }
    }
    get count() {
      return this._count;
    }
    set count(count) {
      if (this._count !== count) {
        this._count = count;
        this.stateChanged.emit(void 0);
      }
    }
    get indent() {
      return this._character.repeat(this._count);
    }
  }
}

export class Toggle extends VDomRenderer<Toggle.Model> {
  constructor(options: Toggle.IOptions) {
    super();
    this.model = new Toggle.Model(options);
  }

  dispose() {
    if (this.isDisposed) {
      return;
    }
    this.model.dispose();
    super.dispose();
  }

  protected render() {
    return (
      <label>
        <span>{this.model.label}</span>
        <input
          type="checkbox"
          defaultChecked={this.model.value}
          onChange={this.handleChange}
        />
      </label>
    );
  }

  handleChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    this.model.value = event.currentTarget.checked;
  };
}

export namespace Toggle {
  export interface IOptions {
    value: boolean;
    label: string;
  }

  export class Model extends VDomModel {
    private _value: boolean;
    private _label: string;

    constructor(options: IOptions) {
      super();
      this._value = options.value;
      this._label = options.label;
    }

    get value() {
      return this._value;
    }
    set value(value) {
      if (this._value !== value) {
        this._value = value;
        this.stateChanged.emit(void 0);
      }
    }
    get label() {
      return this._label;
    }
    set label(label) {
      if (this._label !== label) {
        this._label = label;
        this.stateChanged.emit(void 0);
      }
    }
  }
}
