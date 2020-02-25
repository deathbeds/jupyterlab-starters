export const NS = 'rjsf';

import { Token } from '@phosphor/coreutils';

import { IWidgetTracker } from '@jupyterlab/apputils';

import { JSONSchemaFormDocument } from './document';

import { DocumentRegistry } from '@jupyterlab/docregistry';

/**
 * The name of the factory that creates editor widgets.
 */
export const FACTORY = 'JSONSchemaForm';

export const ICON = 'jp-JsonSchemaFormIcon';

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
  iconClass: `jp-MaterialIcon ${ICON}`,
  fileFormat: 'json',
  contentType: 'file'
};

export const CommandIds = {
  createNew: `${NS}:create-new`
};

export { ICON_SVG };
