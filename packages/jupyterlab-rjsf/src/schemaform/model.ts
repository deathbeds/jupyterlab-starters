import { VDomModel } from '@jupyterlab/apputils';
import { RenderedMarkdown } from '@jupyterlab/rendermime';
import { JSONObject, JSONValue } from '@lumino/coreutils';
import { ISignal, Signal } from '@lumino/signaling';
import { FormProps } from '@rjsf/core';
import { UiSchema, RJSFValidationError } from '@rjsf/utils';

export class SchemaFormModel<T extends JSONValue> extends VDomModel {
  constructor(
    schema: JSONObject,
    props?: Partial<FormProps<T>>,
    options?: SchemaFormModel.IOptions
  ) {
    super();
    this.schema = schema;
    if (props) {
      this.props = props;
      if (props.formData) {
        this._formData = props.formData;
      }
    }
    if (options) {
      this._markdown = options.markdown || null;
      this._liveMarkdown =
        options.liveMarkdown != null ? options.liveMarkdown : this._liveMarkdown;
    }
  }

  /**
   * Get the validation errors for the current form, as defined by the schema
   */
  get errors(): RJSFValidationError[] {
    return this._errors;
  }

  /**
   * Set the validation errors for the current form
   *
   * This should be considered read-only (to be written by the form onChange)
   */
  set errors(errors: RJSFValidationError[]) {
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

  set uiSchema(uiSchema: UiSchema | undefined) {
    this._props.uiSchema = uiSchema;
    this.stateChanged.emit(void 0);
  }

  get uiSchema(): UiSchema | undefined {
    return this._props.uiSchema;
  }

  /**
   * Get the props for the form
   */
  get props(): Partial<FormProps<T>> {
    return this._props;
  }

  /**
   * Set the props for the form
   */
  set props(props: Partial<FormProps<T>>) {
    this._props = props;
    this.stateChanged.emit(void 0);
  }

  get errorsObserved(): boolean {
    return this._errorsObserved;
  }

  set errorsObserved(errorsObserved: boolean) {
    if (errorsObserved !== this._errorsObserved) {
      this._errorsObserved = errorsObserved;
      this.stateChanged.emit(void 0);
    }
  }

  get rendered(): ISignal<SchemaFormModel<T>, void> {
    return this._rendered;
  }

  emitRenderered(): void {
    this._rendered.emit(void 0);
  }

  get markdown(): RenderedMarkdown | null {
    return this._markdown;
  }

  get liveMarkdown(): boolean {
    return this._liveMarkdown;
  }

  set liveMarkdown(liveMarkdown: boolean) {
    this._liveMarkdown = liveMarkdown;
    this.stateChanged.emit(void 0);
  }

  private _formData: T;
  private _errors: RJSFValidationError[] = [];
  private _schema: JSONObject;
  private _props: Partial<FormProps<T>>;
  private _errorsObserved = false;
  private _rendered = new Signal<SchemaFormModel<T>, void>(this);
  private _markdown: RenderedMarkdown | null;
  private _liveMarkdown = false;
}

export namespace SchemaFormModel {
  export interface IOptions {
    markdown?: RenderedMarkdown;
    liveMarkdown?: boolean;
  }
}
