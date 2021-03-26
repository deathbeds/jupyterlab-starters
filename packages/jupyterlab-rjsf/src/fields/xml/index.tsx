import * as React from 'react';

import { CodeMirrorField } from '../codemirror';

export function XMLField(props: any) {
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
