import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import '../style/index.css';

import { NS } from './tokens';

const plugin: JupyterFrontEndPlugin<void> = {
  id: `${NS}:plugin`,
  requires: [],
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    console.log('activated');
  }
};

export default plugin;
