import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
  ILabShell
} from '@jupyterlab/application';
import { ILauncher } from '@jupyterlab/launcher';
import { IIconRegistry } from '@jupyterlab/ui-components';
import { IRenderMimeRegistry } from '@jupyterlab/rendermime';

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
import { NotebookStarter } from './notebookbutton';
import * as SCHEMA from './_schema';

import { NotebookMetadata } from './widgets/meta';
import { BodyBuilder } from './widgets/builder';

const plugin: JupyterFrontEndPlugin<void> = {
  id: `${NS}:plugin`,
  requires: [
    ILabShell,
    ILauncher,
    IIconRegistry,
    INotebookTracker,
    IRenderMimeRegistry
  ],
  autoStart: true,
  activate: (
    app: JupyterFrontEnd,
    shell: ILabShell,
    launcher: ILauncher,
    icons: IIconRegistry,
    notebooks: INotebookTracker,
    rendermime: IRenderMimeRegistry
  ) => {
    const { commands } = app;
    const manager: IStarterManager = new StarterManager({ icons, rendermime });

    commands.addCommand(CommandIDs.start, {
      execute: async (args: any) => {
        const context = (args as any) as IStartContext;
        const { starter, name, cwd, body } = context;

        const runCommands = async (response: SCHEMA.StartResponse) => {
          const starterCommands = response?.starter?.commands;
          if (starterCommands) {
            for (const cmd of starterCommands) {
              await commands.execute(cmd.id, cmd.args);
            }
          } else if (response.status === 'done' && response.path.length) {
            await commands.execute('filebrowser:open-path', {
              path: response.path
            });
          }
        };

        if (starter.schema && !body) {
          const content = new BodyBuilder({ manager, context, name });
          content.id = `id-jp-starters-${name}`;
          app.shell.add(content, 'right');
          shell.expandRight();
          shell.activateById(content.id);
          content.model.start.connect(async (builder, context) => {
            const response = (await commands.execute(
              CommandIDs.start,
              context as any
            )) as SCHEMA.StartResponse;
            switch (response.status) {
              case 'done':
                content.dispose();
                await runCommands(response);
                break;
              case 'continuing':
                content.model.context = {
                  starter: response.starter,
                  name: response.name,
                  body: response.body,
                  cwd: response.path
                };
                await runCommands(response);
                break;
              default:
                console.error(`Unknown status ${response.status}`, response);
            }
          });
        } else if (starter.schema && body) {
          return await manager.start(name, starter, cwd, body);
        } else {
          const response = await manager.start(name, starter, cwd, body);
          await runCommands(response);
        }
      },
      label: (args: any) => args.starter.label,
      caption: (args: any) => args.starter.description,
      iconClass: (args: any) => {
        const context = (args as any) as IStartContext;
        return manager.iconClass(context.name, context.starter);
      }
    });

    let metadata: NotebookMetadata;

    const onCurrentNotebook = () => {
      const { currentWidget } = notebooks;
      if (!currentWidget) {
        if (metadata) {
          metadata.dispose();
        }
        metadata = null;
        notebooks.currentChanged.disconnect(onCurrentNotebook);
      } else {
        metadata.model.notebook = currentWidget;
      }
    };

    commands.addCommand(CommandIDs.notebookMeta, {
      execute: (args: any) => {
        const notebook: NotebookPanel = args.current || notebooks.currentWidget;
        if (!metadata) {
          metadata = new NotebookMetadata({ manager, commands });
          metadata.id = 'id-jp-starters-notebookmeta';
          metadata.title.iconClass = DEFAULT_ICON_CLASS;
          metadata.title.caption = 'Starter Notebook Metadata';
          app.shell.add(metadata, 'right');
          notebooks.currentChanged.connect(onCurrentNotebook);
          metadata.model.notebook = notebook;
          shell.expandRight();
          shell.activateById(metadata.id);
        }
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
