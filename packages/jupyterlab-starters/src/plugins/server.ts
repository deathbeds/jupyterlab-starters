import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';

import { ServerStarterProvider } from '../providers/server';
import { ServerStarterRunner } from '../runners/server';
import { IStarterManager, PKG, SERVER_NAME } from '../tokens';

export const serverProviderPlugin: JupyterFrontEndPlugin<void> = {
  id: `${PKG.name}:server-provider`,
  requires: [IStarterManager],
  autoStart: true,
  activate: (app: JupyterFrontEnd, manager: IStarterManager) => {
    const provider = new ServerStarterProvider();
    manager.addProvider(SERVER_NAME, provider);
  },
};

export const serverRunnerPlugin: JupyterFrontEndPlugin<void> = {
  id: `${PKG.name}:server-runner`,
  requires: [IStarterManager],
  autoStart: true,
  activate: (app: JupyterFrontEnd, manager: IStarterManager) => {
    const runner = new ServerStarterRunner({ manager });
    manager.addRunner(SERVER_NAME, runner);
  },
};
