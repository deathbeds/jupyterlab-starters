import * as React from 'react';

import { CodeMirrorField } from '../codemirror';

export function MarkdownField(props: any) {
  const finalProps = {
    ...props,
    options: {
      ...(props.options || {}),
      cmOptions: {
        ...(props.options?.cmOptions || {}),
        mode: 'text/x-ipythongfm'
      }
    }
  };
  return <CodeMirrorField {...finalProps}></CodeMirrorField>;
}
