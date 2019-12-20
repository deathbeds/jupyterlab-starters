import React from 'react';

import * as rjsf from 'react-jsonschema-form';

import { JSONObject, JSONValue } from '@phosphor/coreutils';

import { Form } from './form';

import { VDomModel, VDomRenderer } from '@jupyterlab/apputils';

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
  SchemaForm.Model<T>
> {
  /**
   * Construct a new Model
   */
  constructor(schema: JSONObject, props: Partial<rjsf.FormProps<T>> = {}) {
    super();
    this._idPrefix = `${SCHEMA_FORM_ID_PREFIX}-${Private.nextId()}`;
    this.model = new SchemaForm.Model<T>(schema, props);
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

/**
 * A namespace for JSON Schema form-related items
 */
export namespace SchemaForm {
  export class Model<T extends JSONValue> extends VDomModel {
    constructor(schema: JSONObject, props?: Partial<rjsf.FormProps<T>>) {
      super();
      this.schema = schema;
      if (props) {
        this.props = props;
      }
    }

    /**
     * Get the validation errors for the current form, as defined by the schema
     */
    get errors(): rjsf.AjvError[] {
      return this._errors;
    }

    /**
     * Set the validation errors for the current form
     *
     * This should be considered read-only (to be written by the form onChange)
     */
    set errors(errors: rjsf.AjvError[]) {
      this._errors = errors;
      this.stateChanged.emit(void 0);
    }

    /**
     * Get the (potentially invalid) form as validated by the schema
     */
    get formData(): T {
      return this._formData;
    }

    /**
     * Set the form data to be validated by the schema
     */
    set formData(formData: T) {
      this._formData = formData;
      this.stateChanged.emit(void 0);
    }

    /**
     * Get the (potentially invalid) form as validated by the schema
     */
    get schema(): JSONObject {
      return this._schema;
    }

    /**
     * Set the form data to be validated by the schema
     */
    set schema(schema: JSONObject) {
      this._schema = schema;
      this.stateChanged.emit(void 0);
    }

    /**
     * Get the props for the form
     */
    get props() {
      return this._props;
    }

    get errorsObserved() {
      return this._errorsObserved;
    }

    set errorsObserved(errorsObserved) {
      if (errorsObserved !== this._errorsObserved) {
        this._errorsObserved = errorsObserved;
        this.stateChanged.emit(void 0);
      }
    }

    /**
     * Set the props for the form
     */
    set props(props) {
      this._props = props;
      this.stateChanged.emit(void 0);
    }

    private _formData: T = null;
    private _errors: rjsf.AjvError[] = [];
    private _schema: JSONObject;
    private _props: Partial<rjsf.FormProps<T>>;
    private _errorsObserved = false;
  }
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
