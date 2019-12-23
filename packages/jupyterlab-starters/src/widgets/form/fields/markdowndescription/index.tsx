import React from 'react';
import marked from 'marked';

import { defaultSanitizer } from '@jupyterlab/apputils';

export class MarkdownDescriptionField extends React.Component<any, any, any> {
  render() {
    const { id, description } = this.props;

    if (!description) {
      return null;
    }

    return (
      <div
        id={id}
        className="field-description jp-RenderedHTMLCommon jp-RenderedMarkdown"
        dangerouslySetInnerHTML={{
          __html: defaultSanitizer
            .sanitize(marked(description))
            .replace(/<a /g, '<a target="_blank" rel="noreferrer" ')
        }}
      ></div>
    );
  }
}
