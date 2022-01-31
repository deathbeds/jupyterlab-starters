import * as React from 'react';

import { CodeMirrorField } from '../codemirror';

export function XMLField(props: Record<string, any>): JSX.Element {
  const finalProps = {
    ...props,
    options: {
      cmOptions: {
        ...(props.options?.cmOptions || {}),
        mode: 'text/xml',
      },
    },
  };
  return <CodeMirrorField {...finalProps}></CodeMirrorField>;
}
