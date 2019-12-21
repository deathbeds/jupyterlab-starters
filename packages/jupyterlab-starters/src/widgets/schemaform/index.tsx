import React from 'react';

import * as rjsf from 'react-jsonschema-form';

import { JSONObject, JSONValue } from '@phosphor/coreutils';
import { VDomRenderer } from '@jupyterlab/apputils';

import { Form } from '../form';

import { SchemaFormModel } from './model';

/**
 * The id prefix all JSON Schema forms will share
 */
const SCHEMA_FORM_ID_PREFIX = 'id-jp-schemaform';

/**
 * The class all JSON Schema forms will share
 */
const SCHEMA_FORM_CLASS = 'jp-SchemaForm';

/**
 * Am opionated widget for displaying a form defined by JSON Schema
 */
export class SchemaForm<T extends JSONValue> extends VDomRenderer<
  SchemaFormModel<T>
> {
  /**
   * Construct a new Model
   */
  constructor(schema: JSONObject, props: Partial<rjsf.FormProps<T>> = {}) {
    super();
    this._idPrefix = `${SCHEMA_FORM_ID_PREFIX}-${Private.nextId()}`;
    this.model = new SchemaFormModel<T>(schema, props);
  }

  /**
   * Render the form, if the model is available
   */
  render() {
    if (!this.model) {
      return null;
    }

    const { schema, props, formData } = this.model;

    const className = `${SCHEMA_FORM_CLASS} ${props.className || ''}`.trim();

    const finalProps = {
      // props from model
      ...props,
      // assure a default prefix
      idPrefix: this._idPrefix,
      schema,
      formData,
      // overload classname
      className,
      validate: (formData: T, errors: rjsf.AjvError[]) => {
        return errors;
      },
      // overload onChange
      onChange: (evt: rjsf.IChangeEvent<T>, err?: rjsf.ErrorSchema) => {
        this.onChange(evt, err);

        if (props.onChange) {
          props.onChange(evt, err);
        }
      }
    };

    setTimeout(this._observeErrors, 100);

    return <Form {...finalProps} />;
  }

  _observeErrors = () => {
    this.model.errorsObserved = !!this.node.querySelector('.errors');
  };

  /**
   * Handle the change of a form by the user and update the model
   */
  onChange(evt: rjsf.IChangeEvent<T>, _err?: rjsf.ErrorSchema) {
    const { formData, errors } = evt;
    if (formData != null) {
      this.model.errors = errors;
      this.model.formData = formData;
    }
    this.model.stateChanged.emit(void 0);
  }

  /**
   * Get the JSON object specified by the user, along with any validation errors
   */
  getValue() {
    return {
      formData: this.model.formData,
      errors: this.model.errors
    };
  }

  /**
   * The id prefix to use for all form children
   */
  private _idPrefix: string;
}

namespace Private {
  let _nextId = 0;

  /**
   * Return the next id to be used for the created form children
   */
  export function nextId() {
    return _nextId++;
  }
}