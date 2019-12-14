import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { ILauncher } from '@jupyterlab/launcher';

import '../style/index.css';
import { StarterManager } from './manager';

import { NS, CommandIDs } from './tokens';

const plugin: JupyterFrontEndPlugin<void> = {
  id: `${NS}:plugin`,
  requires: [ILauncher],
  autoStart: true,
  activate: (app: JupyterFrontEnd, launcher: ILauncher) => {
    const { commands } = app;
    const manager = new StarterManager();

    commands.addCommand(CommandIDs.copy, {
      execute: async (args: any) => {
        await manager.copy(args.name, args.cwd);
      },
      label: (args: any) => {
        return manager.starter(args.name).label;
      }
    });

    manager.changed.connect(() => {
      const { starters } = manager;
      for (const name in starters) {
        launcher.add({
          command: CommandIDs.copy,
          args: { name }
        });
      }
    });

    manager.fetch().catch(console.warn);
  }
};

export default plugin;
