import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { ILauncher } from '@jupyterlab/launcher';
import { IIconRegistry } from '@jupyterlab/ui-components';
import { MainAreaWidget } from '@jupyterlab/apputils';

import '../style/index.css';

import { StarterManager } from './manager';

import {
  NS,
  CommandIDs,
  CATEGORY,
  IStartContext,
  IStarterManager
} from './tokens';
import { BodyBuilder } from './bodybuilder';

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
    const manager: IStarterManager = new StarterManager({ icons });

    commands.addCommand(CommandIDs.start, {
      execute: async (args: any) => {
        const context = (args as any) as IStartContext;
        const { starter, name, cwd, body } = context;

        if (starter.schema && !body) {
          const content = new BodyBuilder({ manager, context });
          const main = new MainAreaWidget({ content });
          app.shell.add(main, 'main', { mode: 'split-right' });
          content.start.connect(async (builder, context) => {
            await commands.execute(CommandIDs.start, context as any);
            main.dispose();
          });
        } else {
          const response = await manager.start(name, cwd, body);

          if (starter.commands) {
            for (const cmd of starter.commands) {
              await commands.execute(cmd.id, cmd.args);
            }
          }

          await commands.execute('filebrowser:open-path', {
            path: response.path
          });
        }
      },
      label: (args: any) => args.starter.label,
      caption: (args: any) => args.starter.description,
      iconClass: (args: any) => {
        const context = (args as any) as IStartContext;
        return manager.iconClass(context.name, context.starter);
      }
    });

    manager.changed.connect(() => {
      const { starters } = manager;
      for (const name in starters) {
        launcher.add({
          command: CommandIDs.start,
          args: { name, starter: starters[name] },
          category: CATEGORY
        });
      }
    });

    manager.fetch().catch(console.warn);
  }
};

export default plugin;
