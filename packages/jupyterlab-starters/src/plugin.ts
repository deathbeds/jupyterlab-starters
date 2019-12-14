import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { ILauncher } from '@jupyterlab/launcher';
import { IIconRegistry } from '@jupyterlab/ui-components';

import '../style/index.css';

import DEFAULT_ICON_SVG from '!!raw-loader!../style/icons/starter.svg';

import { StarterManager } from './manager';

import { NS, CommandIDs } from './tokens';

export const DEFAULT_ICON_NAME = `${NS}-default`;
export const DEFAULT_ICON_CLASS = `jp-StartersDefaultIcon`;
export const CATEGORY = 'Starters';

const plugin: JupyterFrontEndPlugin<void> = {
  id: `${NS}:plugin`,
  requires: [ILauncher, IIconRegistry],
  autoStart: true,
  activate: (
    app: JupyterFrontEnd,
    launcher: ILauncher,
    icons: IIconRegistry
  ) => {
    const { commands } = app;
    const manager = new StarterManager();
    const icon = { name: DEFAULT_ICON_NAME, svg: DEFAULT_ICON_SVG };
    console.log(icon);
    icons.addIcon(icon);

    commands.addCommand(CommandIDs.copy, {
      execute: async (args: any) => {
        console.log(args);
        await manager.copy(args.name, args.cwd);
        if (args.starter.commands) {
          for (const cmd of args.starter.commands) {
            await commands.execute(cmd.id, cmd.args);
          }
        }
      },
      label: (args: any) => args.starter.label,
      caption: (args: any) => args.starter.description,
      iconClass: (args: any) => args.starter.icon || DEFAULT_ICON_CLASS
    });

    manager.changed.connect(() => {
      const { starters } = manager;
      for (const name in starters) {
        launcher.add({
          command: CommandIDs.copy,
          args: { name, starter: starters[name] },
          category: CATEGORY
        });
      }
    });

    manager.fetch().catch(console.warn);
  }
};

export default plugin;
