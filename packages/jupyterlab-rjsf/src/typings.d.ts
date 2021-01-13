declare module '*.svg' {
  const script: string;
  export default script;
}

declare module '@rjsf/core/lib/components/fields/ObjectField' {
  import * as React from 'react';
  import * as rjsf from '@rjsf/core';

  export default class ObjectField extends React.Component<any, any, any> {}
}

declare module '@rjsf/core/lib/components/fields/StringField' {
  import * as React from 'react';
  import * as rjsf from '@rjsf/core';

  export default class StringField extends React.Component<any, any, any> {}
}
