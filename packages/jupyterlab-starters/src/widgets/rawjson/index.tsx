import * as React from 'react';

import ObjectField from 'react-jsonschema-form/lib/components/fields/ObjectField';

import * as rjsfUtils from 'react-jsonschema-form/lib/utils';

import { UnControlled } from 'react-codemirror2';

import * as CodeMirror from 'codemirror';

import { JSONExt } from '@phosphor/coreutils';

export class RawJSONObjectField extends ObjectField {
  protected _editor: CodeMirror.Editor;

  render() {
    const {
      uiSchema,
      formData,
      idSchema,
      name,
      registry = rjsfUtils.getDefaultRegistry()
    } = this.props;
    const { definitions } = registry;
    const schema = (rjsfUtils as any).retrieveSchema(
      this.props.schema,
      definitions,
      formData
    );

    let title;
    if (this.state.wasPropertyKeyModified) {
      title = name;
    } else {
      title = schema.title === undefined ? name : schema.title;
    }

    const isLight = !!document.querySelector('body[data-jp-theme-light="true"]');

    const description = uiSchema['ui:description'] || schema.description;
    const { canSave } = this;
    const saveClassName = `jp-mod-styled ${canSave ? 'jp-mod-accept' : ''}`;

    return (
      <>
        <legend>{title}</legend>
        <p className="field-description">{description}</p>
        <button
          disabled={!canSave}
          className={saveClassName}
          onClick={this.onSave}
        >
          Save
        </button>
        <button className="jp-mod-styled" onClick={this.onReset}>
          Reset
        </button>
        <div id={idSchema.$id}>
          <UnControlled
            editorDidMount={editor => (this._editor = editor)}
            value={JSON.stringify(formData, null, 2)}
            options={{
              mode: 'application/json',
              theme: isLight ? 'default' : 'zenburn'
            }}
            onChange={this.onChange}
          />
        </div>
      </>
    );
  }

  get canSave() {
    return (
      !this.state.editorError &&
      this.state.editorValue &&
      !JSONExt.deepEqual(this.state.editorValue, this.props.formData)
    );
  }

  onReset = () => {
    this._editor
      .getDoc()
      .setValue(JSON.stringify(this.props.formData, null, 2));
  };

  onSave = () => {
    this.props.onChange(this.state.editorValue);
  };

  onChange = (editor: CodeMirror.Editor, data: any, value: string) => {
    try {
      const jsonValue = JSON.parse(value);
      this.setState({ editorValue: jsonValue, editorError: false });
    } catch (err) {
      this.setState({ editorValue: null, editorError: true });
    }
  };
}
