import * as React from 'react';

/* order might matter on these imports */
/* first core... */
import { utils as rjsfUtils } from '@rjsf/core';

/* ...then lib imports */
import _ObjectField from '@rjsf/core/lib/components/fields/ObjectField';

import { UnControlled } from 'react-codemirror2';

import * as CodeMirror from 'codemirror';

import { JSONExt } from '@lumino/coreutils';

/**
 * This is a pretty nasty way to deal with the ObjectField being very hard
 * to reach at import time
 *
 * We use the upstream ObjectField at runtime to construct a private class.
 * This could likely be improved with a namespace or something.
 */
export function makeJSONObjectField(ObjectField: typeof _ObjectField) {
  /**
   * A raw JSON Object which can be stored/edited inside an RJSF
   */
  class JSONObjectField extends ObjectField {
    protected _editor: CodeMirror.Editor;

    render() {
      const {
        uiSchema,
        formData,
        idSchema,
        name,
        registry = rjsfUtils.getDefaultRegistry(),
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

      const isLight = !!document.querySelector(
        'body[data-jp-theme-light="true"]'
      );

      const description = uiSchema['ui:description'] || schema.description;
      const { canSave } = this;

      const options = {
        mode: 'application/json',
        theme: isLight ? 'default' : 'zenburn',
        matchBrackets: true,
        autoCloseBrackets: true,
      };

      return (
        <>
          <legend>{title}</legend>
          <p className="field-description">{description}</p>
          <div className="jp-SchemaForm-JSONObject-buttons">
            <button
              id={`${idSchema.$id}_revert`}
              className="jp-JSONEditor-revertButton"
              title="Revert to Previous Notebook Metadata"
              onClick={this.onReset}
            ></button>
            <button
              id={`${idSchema.$id}_commit`}
              disabled={!canSave}
              className="jp-JSONEditor-commitButton"
              title="Commit to Notebook Metadata"
              onClick={this.onSave}
            ></button>
          </div>
          <div id={idSchema.$id}>
            <UnControlled
              editorDidMount={(editor) => (this._editor = editor)}
              value={JSON.stringify(formData, null, 2)}
              options={options}
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

  return JSONObjectField as any;
}
