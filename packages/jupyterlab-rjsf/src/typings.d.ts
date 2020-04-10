declare module '!!raw-loader!*.svg' {
  const script: string;
  export default script;
}

declare module 'react-jsonschema-form/lib/components/fields/ObjectField' {
  import * as React from 'react';
  export default class ObjectField extends React.Component<any, any, any> {}
}

declare module 'react-jsonschema-form/lib/components/fields/StringField' {
  import * as React from 'react';
  export default class StringField extends React.Component<any, any, any> {}
}
