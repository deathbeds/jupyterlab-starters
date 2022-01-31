import * as React from 'react';

import { UnControlled } from 'react-codemirror2';

import type CodeMirror from 'codemirror';

export function CodeMirrorField(props: Record<string, any>): JSX.Element {
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

export function codeMirrorDefaults(): Record<string, any> {
  const isLight = !!document.querySelector('body[data-jp-theme-light="true"]');

  return {
    theme: isLight ? 'default' : 'zenburn',
    matchBrackets: true,
    autoCloseBrackets: true,
    lineWrapping: true,
  };
}
