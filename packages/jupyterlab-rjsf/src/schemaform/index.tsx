import { VDomRenderer } from '@jupyterlab/apputils';
import { renderMarkdown } from '@jupyterlab/rendermime/lib/renderers';
import { JSONObject, JSONValue } from '@lumino/coreutils';
import { FormProps, IChangeEvent } from '@rjsf/core';
import { RJSFValidationError } from '@rjsf/utils';
import validatorAjv8 from '@rjsf/validator-ajv8';
import React from 'react';

import { Form } from '../form';

import { SchemaFormModel } from './model';

const MARKDOWN_CLASSES = ['jp-RenderedMarkdown', 'jp-RenderedHTMLCommon'];
const RENDERABLE_LABELS = [
  'legend',
  '.field-description',
  '.control-label',
  '.help-block',
  '.field-radio-group .radio > label > span > span',
  '.field-boolean .checkbox > label > span',
];
const ALL_LABELS = RENDERABLE_LABELS.join(', ');
const UNRENDERED_LABELS = RENDERABLE_LABELS.map(
  (s) => `${s}:not(.jp-RenderedMarkdown)`
).join(', ');

/**
 * The id prefix all JSON Schema forms will share
 */
const SCHEMA_FORM_ID_PREFIX = 'id-jp-schemaform';

/**
 * The class all JSON Schema forms will share
 */
const SCHEMA_FORM_CLASS = 'jp-SchemaForm';

/**
 * The class all JSON Schema form wrapper widgets will share
 */
const SCHEMA_FORM_WIDGET_CLASS = 'jp-SchemaForm-Widget';

/**
 *
 */
const MARKDOWN_CANARY = 'jp-SchemaForm-markdown';

/**
 * Am opionated widget for displaying a form defined by JSON Schema
 */
export class SchemaForm<T extends JSONValue = JSONValue> extends VDomRenderer<
  SchemaFormModel<T>
> {
  /**
   * Construct a new Model
   */
  constructor(
    schema: JSONObject,
    props: Partial<FormProps<T>> = {},
    options?: SchemaFormModel.IOptions
  ) {
    super(new SchemaFormModel<T>(schema, props, options));
    this.addClass(SCHEMA_FORM_WIDGET_CLASS);
    this._idPrefix = `${SCHEMA_FORM_ID_PREFIX}-${Private.nextId()}`;
    if (this.model.markdown) {
      this.model.rendered.connect(this._renderMarkdown);
    }
  }

  /**
   * Render the form, if the model is available
   */
  render(): JSX.Element | null {
    if (!this.model) {
      return null;
    }

    const { schema, props, formData } = this.model;

    const className = `${SCHEMA_FORM_CLASS} ${props.className || ''}`.trim();

    const finalProps = {
      // props from model
      ...props,
      // ensure a validator
      validator: props.validator || validatorAjv8,
      // assure a default prefix
      idPrefix: this._idPrefix,
      schema,
      formData,
      // overload classname
      className,
      validate: (formData: T, errors: RJSFValidationError[]) => {
        return errors;
      },
      // overload onChange
      onChange: (evt: IChangeEvent<T>) => {
        this.onChange(evt);

        if (props.onChange) {
          props.onChange(evt);
        }
      },
    };

    setTimeout(this._postRender, 100);

    return <Form {...finalProps} />;
  }

  /**
   * Handle the change of a form by the user and update the model
   */
  onChange(evt: IChangeEvent<T>): void {
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
  getValue(): SchemaForm.IValue<T> {
    return {
      formData: this.model.formData,
      errors: this.model.errors,
    };
  }

  protected _renderMarkdown = async (): Promise<void> => {
    const hosts: HTMLElement[] = Array.from(
      this.node.querySelectorAll(
        this.model.liveMarkdown ? UNRENDERED_LABELS : ALL_LABELS
      )
    );
    if (!hosts.length && !this._initialRender) {
      this._initialRenderDelay = this._initialRenderDelay * 2;
      setTimeout(this._renderMarkdown, this._initialRenderDelay);
      return;
    }
    this._initialRender = true;
    await Promise.all(hosts.map(this._renderOneMarkdown));
  };

  protected _renderOneMarkdown = async (host: HTMLElement): Promise<void> => {
    if (host.querySelector(`.${MARKDOWN_CANARY}`)) {
      return;
    }
    const markdown = this.model.markdown;
    if (markdown == null) {
      return;
    }
    const { textContent, dataset } = host;
    const { rawMarkdown } = dataset;
    const source = rawMarkdown || textContent;
    if (source == null || !source.trim()) {
      return;
    }

    if (textContent) {
      dataset.rawMarkdown = textContent;
    }

    host.classList.add(...MARKDOWN_CLASSES);

    await renderMarkdown({
      host: host as HTMLElement,
      source: rawMarkdown || textContent || '',
      trusted: true,
      sanitizer: markdown.sanitizer,
      latexTypesetter: markdown.latexTypesetter,
      resolver: markdown.resolver,
      linkHandler: markdown.linkHandler,
      shouldTypeset: true,
    });

    const canary = document.createElement('span');
    canary.className = MARKDOWN_CANARY;

    host.appendChild(canary);
  };

  protected _postRender = (): void => {
    this.model.errorsObserved = !!this.node.querySelector('.errors');
    this.model.emitRenderered();
  };

  /**
   * The id prefix to use for all form children
   */
  private _idPrefix: string;
  private _initialRender = false;
  private _initialRenderDelay = 10;
}

export namespace SchemaForm {
  export interface IValue<T extends JSONValue> {
    formData: T;
    errors: RJSFValidationError[];
  }
}

namespace Private {
  let _nextId = 0;

  /**
   * Return the next id to be used for the created form children
   */
  export function nextId(): number {
    return _nextId++;
  }
}
