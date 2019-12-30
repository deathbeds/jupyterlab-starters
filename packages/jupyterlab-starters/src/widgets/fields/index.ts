import { CodeMirrorField } from './codemirror';
import { JSONObjectField } from './jsonobject';
import { MarkdownField } from './markdown';
import { XMLField } from './xml';

export const CUSTOM_UI_WIDGETS = {
  'codemirror-xml': XMLField,
  codemirror: CodeMirrorField,
  'codemirror-markdown': MarkdownField
};

export const CUSTOM_UI_FIELDS = {
  'codemirror-jsonobject': JSONObjectField
};

export const ALL_CUSTOM_UI = {
  fields: CUSTOM_UI_FIELDS,
  widgets: CUSTOM_UI_WIDGETS
};

export { CodeMirrorField, JSONObjectField, MarkdownField, XMLField };

export const AS_JSONOBJECT = { 'ui:field': 'codemirror-jsonobject' };
export const AS_TEXTAREA = { 'ui:widget': 'textarea' };
export const AS_XML = { 'ui:widget': 'codemirror-xml' };
export const AS_MARKDOWN = { 'ui:widget': 'codemirror-markdown' };
