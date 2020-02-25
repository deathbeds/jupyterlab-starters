export const NS = 'rjsf';

import { Token } from '@phosphor/coreutils';
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

export const FILE_TYPE: DocumentRegistry.IFileType = {
  name: 'rjsf',
  displayName: 'JSON Schema Form',
  mimeTypes: ['application/json'],
  extensions: ['.json'],
  iconClass: ICON_CLASS,
  fileFormat: 'json',
  contentType: 'file'
};

export const CommandIds = {
  createNew: `${NS}:create-new`
};

export interface ISchemaManager {
  widgetsChanged: ISignal<ISchemaManager, void>;
  widgets: Widget[];
  markdown: RenderedMarkdown;
}

export { ICON_SVG };
