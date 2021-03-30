import * as React from 'react';

import { UnControlled } from 'react-codemirror2';

export function CodeMirrorField(props: any) {
  const { options } = props;

  const cmOptions = {
    ...codeMirrorDefaults(),
    ...(options?.cmOptions || {}),
  };

  const onChange = (editor: CodeMirror.Editor, data: any, value: string) => {
    props.onChange(value);
  };

  return (
    <>
      <div>
        <UnControlled
          value={props.value}
          options={cmOptions}
          onChange={onChange}
          autoCursor={false}
          autoScroll={false}
        />
      </div>
    </>
  );
}

export function codeMirrorDefaults() {
  const isLight = !!document.querySelector('body[data-jp-theme-light="true"]');

  return {
    theme: isLight ? 'default' : 'zenburn',
    matchBrackets: true,
    autoCloseBrackets: true,
    lineWrapping: true,
  };
}
