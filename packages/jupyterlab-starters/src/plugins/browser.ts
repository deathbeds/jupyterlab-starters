import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { SettingsProvider } from '../providers/settings';
import { BrowserStarterRunner } from '../runners/browser';
import { IStarterManager, SETTINGS_PLUGIN_ID, PKG, SETTINGS_NAME } from '../tokens';

export const settingsProviderPlugin: JupyterFrontEndPlugin<void> = {
  id: SETTINGS_PLUGIN_ID,
  requires: [IStarterManager, ISettingRegistry],
  autoStart: true,
  activate: (
    app: JupyterFrontEnd,
    manager: IStarterManager,
    settingRegistry: ISettingRegistry
  ) => {
    const provider = new SettingsProvider({
      settingsGetter: async () => {
        const { composite } = await settingRegistry.load(SETTINGS_PLUGIN_ID);
        return composite;
      },
    });
    manager.addProvider(SETTINGS_NAME, provider);
  },
};

export const browserRunnerPlugin: JupyterFrontEndPlugin<void> = {
  id: `${PKG.name}:browser-runner`,
  requires: [IStarterManager],
  autoStart: true,
  activate: (app: JupyterFrontEnd, manager: IStarterManager) => {
    const { contents } = app.serviceManager;
    const runner = new BrowserStarterRunner({ manager, contents });
    manager.addRunner('browser', runner);
  },
};
