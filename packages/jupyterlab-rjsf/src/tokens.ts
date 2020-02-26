export const NS = 'rjsf';

import { Token, JSONObject } from '@phosphor/coreutils';
import { ISignal } from '@phosphor/signaling';
import { Widget } from '@phosphor/widgets';
import { IWidgetTracker } from '@jupyterlab/apputils';
import { RenderedMarkdown } from '@jupyterlab/rendermime';

import { JSONSchemaFormDocument } from './document';

import { DocumentRegistry } from '@jupyterlab/docregistry';

/**
 * The name of the factory that creates editor widgets.
 */
export const FACTORY = 'Schema Form';

export const ICON_CLASS = 'jp-JsonSchemaFormIcon';

export const ICON_NAME = 'json-schema-form';

import ICON_SVG from '!!raw-loader!../style/icons/form.svg';

export interface IJSONSchemaFormTracker
  extends IWidgetTracker<JSONSchemaFormDocument> {}

export const IJSONSchemaFormTracker = new Token<IJSONSchemaFormTracker>(
  `${NS}/tracker`
);

export interface IFileTypes {
  [key: string]: DocumentRegistry.IFileType;
}

export const FILE_TYPES: IFileTypes = {
  'rjsf-json-instance': {
    name: 'json',
    displayName: 'JSON Schema Form',
    mimeTypes: ['application/json', 'application/schema-instance+json'],
    extensions: ['.json', '.instance.json'],
    iconClass: ICON_CLASS,
    fileFormat: 'json',
    contentType: 'file'
  },
  'rjsf-yaml-instance': {
    name: 'yaml',
    displayName: 'JSON Schema Form in YAML',
    mimeTypes: ['text/yaml', 'text/schema-instance+yaml'],
    extensions: ['.yaml', '.yml', '.instance.yaml', '.instance.yml'],
    iconClass: ICON_CLASS,
    fileFormat: 'json',
    contentType: 'file'
  }
};

export const CommandIds = {
  createNew: `${NS}:create-new`
};

export interface ISchemaManager extends ISchemaManager.IFullIO {
  widgetsChanged: ISignal<ISchemaManager, void>;
  widgets: Widget[];
  markdown: RenderedMarkdown;
  registerReader(matcher: ISchemaManager.IContextMatcher): void;
  registerWriter(matcher: ISchemaManager.IContextMatcher): void;
  isActive(widget: Widget): boolean;
}

export namespace ISchemaManager {
  export interface IContextMatcher {
    handles<T>(action: string, context: DocumentRegistry.Context): boolean;
  }
  export interface IReader extends IContextMatcher {
    read(context: DocumentRegistry.Context): Promise<JSONObject>;
  }
  export interface IWriter extends IContextMatcher {
    write(value: JSONObject, context: DocumentRegistry.Context): Promise<void>;
  }
  export interface IFullIO extends IContextMatcher, IReader, IWriter {}
}

export { ICON_SVG };
