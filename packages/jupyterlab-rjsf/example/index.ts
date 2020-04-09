import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { MainAreaWidget } from '@jupyterlab/apputils';

import { IRenderMimeRegistry, RenderedMarkdown } from '@jupyterlab/rendermime';

import { SchemaForm } from '@deathbeds/jupyterlab-rjsf/lib/schemaform';
import { ALL_CUSTOM_UI } from '@deathbeds/jupyterlab-rjsf/lib/fields';

import * as SCHEMA from './schema.json';

const plugin: JupyterFrontEndPlugin<void> = {
  id: `jupyterlab-rjsf-hello-world:plugin`,
  requires: [JupyterFrontEnd.IPaths, IRenderMimeRegistry],
  autoStart: true,
  activate: (app: JupyterFrontEnd, rendermime: IRenderMimeRegistry) => {
    const props = {
      liveValidate: true,
      formData: { name: 'World' },
      ...ALL_CUSTOM_UI
    };
    const options = {
      markdown: rendermime.createRenderer('text/markdown') as RenderedMarkdown
    };
    const main = new MainAreaWidget({
      content: new SchemaForm(SCHEMA, props, options)
    });
    main.title.label = 'Hello World';
    app.shell.add(main, 'main');
  }
};
