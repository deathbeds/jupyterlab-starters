import * as React from 'react';

import { CodeMirrorField } from '../codemirror';

export function MarkdownField(props: Record<string, any>): JSX.Element {
  const finalProps = {
    ...props,
    options: {
      ...(props.options || {}),
      cmOptions: {
        ...(props.options?.cmOptions || {}),
        mode: 'text/x-ipythongfm',
      },
    },
  };
  return <CodeMirrorField {...finalProps}></CodeMirrorField>;
}
