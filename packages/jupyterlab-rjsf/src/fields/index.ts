/**
 * An unfortunately very convoluted way to expose some custom react components
 * in the face of federated modules
 */
import { FormProps, utils, Field, Widget } from '@rjsf/core';
import React from 'react';

export type TComponentFactory = (props: Record<string, any>) => JSX.Element;
export type TComponentMap = Record<string, TComponentFactory | React.ComponentClass>;

/**
 * a subset of an RJSF `widgets` prop
 */
export const CUSTOM_UI_WIDGETS = async (): Promise<FormProps<any>['widgets']> => {
  const widgets = {
    'codemirror-xml': await XMLField(),
    codemirror: await CodeMirrorField(),
    'codemirror-markdown': await MarkdownField(),
  };

  return widgets;
};

/**
 * a subset of an RJSF `fields` prop
 */
export const CUSTOM_UI_FIELDS = async (): Promise<FormProps<any>['fields']> => {
  const fields = {
    'codemirror-jsonobject': await JSONObjectField(),
  };

  return fields as any;
};

/**
 * a subset of an RJSF props with all custom elements available
 */
export const ALL_CUSTOM_UI = async (): Promise<Partial<FormProps<any>>> => {
  return {
    fields: await CUSTOM_UI_FIELDS(),
    widgets: await CUSTOM_UI_WIDGETS(),
  };
};

/**
 * janky lazy references to Field classes
 */
export const CodeMirrorField = async (): Promise<Widget> =>
  (await import('./codemirror')).CodeMirrorField;
export const MarkdownField = async (): Promise<Widget> =>
  (await import('./markdown')).MarkdownField;
export const XMLField = async (): Promise<Widget> => (await import('./xml')).XMLField;
export const JSONObjectField = async (): Promise<Field> => {
  const reg = utils.getDefaultRegistry();
  return (await import('./jsonobject')).makeJSONObjectField(
    reg.fields['ObjectField'] as any
  );
};

/**
 * the RJSF uiSchema for activating these components
 */
export const AS_JSONOBJECT = { 'ui:field': 'codemirror-jsonobject' };
export const AS_TEXTAREA = { 'ui:widget': 'textarea' };
export const AS_XML = { 'ui:widget': 'codemirror-xml' };
export const AS_MARKDOWN = { 'ui:widget': 'codemirror-markdown' };
