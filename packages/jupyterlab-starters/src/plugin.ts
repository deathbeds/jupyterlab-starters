import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { ILauncher } from '@jupyterlab/launcher';
import { IIconRegistry } from '@jupyterlab/ui-components';
import { MainAreaWidget } from '@jupyterlab/apputils';

import { NotebookPanel, INotebookTracker } from '@jupyterlab/notebook';

import '../style/index.css';

import { StarterManager } from './manager';

import {
  NS,
  CommandIDs,
  CATEGORY,
  IStartContext,
  IStarterManager,
  DEFAULT_ICON_CLASS
} from './tokens';
import { BodyBuilder } from './bodybuilder';
import { NotebookStarter } from './notebookbutton';
import * as SCHEMA from './_schema';

const plugin: JupyterFrontEndPlugin<void> = {
  id: `${NS}:plugin`,
  requires: [ILauncher, IIconRegistry, INotebookTracker],
  autoStart: true,
  activate: (
    app: JupyterFrontEnd,
    launcher: ILauncher,
    icons: IIconRegistry,
    notebooks: INotebookTracker
  ) => {
    const { commands } = app;
    const manager: IStarterManager = new StarterManager({ icons });

    commands.addCommand(CommandIDs.start, {
      execute: async (args: any) => {
        const context = (args as any) as IStartContext;
        const { starter, name, cwd, body } = context;

        if (starter.schema && !body) {
          const content = new BodyBuilder({ manager, context, name });
          const main = new MainAreaWidget({ content });
          app.shell.add(main, 'main', { mode: 'split-right' });
          content.model.start.connect(async (builder, context) => {
            const response = (await commands.execute(
              CommandIDs.start,
              context as any
            )) as SCHEMA.StartResponse;
            switch (response.status) {
              case 'done':
                main.dispose();
                await commands.execute('filebrowser:open-path', {
                  path: response.path
                });
                break;
              case 'continuing':
                content.model.context = {
                  starter: response.starter,
                  name: response.name,
                  body: response.body,
                  cwd: response.path
                };
                break;
              default:
                console.error(`Unknown status ${response.status}`, response);
            }
          });
        } else if (starter.schema && body) {
          return await manager.start(name, starter, cwd, body);
        } else {
          const response = await manager.start(name, starter, cwd, body);

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

    commands.addCommand(CommandIDs.notebookMeta, {
      execute: (args: any) => {
        const notebook: NotebookPanel = args.current || notebooks.currentWidget;
        console.log(notebook);
      },
      caption: (args: any) => {
        const notebook: NotebookPanel = args.current || notebooks.currentWidget;
        if (!notebook) {
          return '';
        }
        return `Configure ${notebook.title.label.replace(
          /.ipynb$/,
          ''
        )} as Starter`;
      },
      iconClass: DEFAULT_ICON_CLASS
    });

    const notebookbutton = new NotebookStarter({ commands });

    app.docRegistry.addWidgetExtension('Notebook', notebookbutton);

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
