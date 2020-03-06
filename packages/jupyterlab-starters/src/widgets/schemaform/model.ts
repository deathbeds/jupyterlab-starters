import * as rjsf from 'react-jsonschema-form';

import { Signal } from '@lumino/signaling';
import { JSONObject, JSONValue } from '@lumino/coreutils';
import { VDomModel } from '@jupyterlab/apputils';
import { RenderedMarkdown } from '@jupyterlab/rendermime';

export class SchemaFormModel<T extends JSONValue> extends VDomModel {
  constructor(
    schema: JSONObject,
    props?: Partial<rjsf.FormProps<T>>,
    options?: SchemaFormModel.IOptions
  ) {
    super();
    this.schema = schema;
    if (props) {
      this.props = props;
    }
    if (options) {
      this._markdown = options.markdown;
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

  set uiSchema(uiSchema: any) {
    this._props.uiSchema = uiSchema;
    this.stateChanged.emit(void 0);
  }

  get uiSchema() {
    return this._props.uiSchema;
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

  get rendered() {
    return this._rendered;
  }

  emitRenderered() {
    this._rendered.emit(void 0);
  }

  get markdown() {
    return this._markdown;
  }

  private _formData: T = null;
  private _errors: rjsf.AjvError[] = [];
  private _schema: JSONObject;
  private _props: Partial<rjsf.FormProps<T>>;
  private _errorsObserved = false;
  private _rendered = new Signal<SchemaFormModel<T>, void>(this);
  private _markdown: RenderedMarkdown;
}

export namespace SchemaFormModel {
  export interface IOptions {
    markdown?: RenderedMarkdown;
  }
}
