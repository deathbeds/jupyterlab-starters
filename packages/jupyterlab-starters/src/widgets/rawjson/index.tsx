import * as React from 'react';

import ObjectField from 'react-jsonschema-form/lib/components/fields/ObjectField';

import * as rjsfUtils from 'react-jsonschema-form/lib/utils';

export class RawJSONObjectField extends ObjectField {
  render() {
    const {
      uiSchema,
      formData,
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

    const description = uiSchema['ui:description'] || schema.description;

    const onChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
      try {
        const value = JSON.parse(event.currentTarget.value);
        this.props.onChange(value);
      } catch (err) {
        //
      }
    };

    return (
      <div>
        <legend>{title}</legend>
        <p className="field-description">{description}</p>
        <textarea
          defaultValue={JSON.stringify(formData, null, 2)}
          onChange={onChange}
        ></textarea>
      </div>
    );
  }
}
