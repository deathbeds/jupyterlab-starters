import { URLExt } from '@jupyterlab/coreutils';
import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
  ILabShell,
  IRouter,
} from '@jupyterlab/application';

import { PageConfig } from '@jupyterlab/coreutils';
import { IRunningSessionManagers } from '@jupyterlab/running';

import { ILauncher } from '@jupyterlab/launcher';
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
  DEFAULT_ICON_CLASS,
} from './tokens';
import { NotebookStarter } from './notebookbutton';
import * as SCHEMA from './_schema';
import { CSS } from './css';

import { NotebookMetadata } from './widgets/meta';
import { BodyBuilder } from './widgets/builder';

const plugin: JupyterFrontEndPlugin<void> = {
  id: `${NS}:plugin`,
  requires: [
    JupyterFrontEnd.IPaths,
    ILabShell,
    ILauncher,
    INotebookTracker,
    IRenderMimeRegistry,
    IRouter,
    IRunningSessionManagers,
  ],
  autoStart: true,
  activate: (
    app: JupyterFrontEnd,
    paths: JupyterFrontEnd.IPaths,
    shell: ILabShell,
    launcher: ILauncher,
    notebooks: INotebookTracker,
    rendermime: IRenderMimeRegistry,
    router: IRouter,
    running: IRunningSessionManagers
  ) => {
    const { commands } = app;
    const manager: IStarterManager = new StarterManager({ rendermime });

    running.add(manager);

    commands.addCommand(CommandIDs.start, {
      execute: async (args: any) => {
        const context = (args as any) as IStartContext;
        const { starter, name, cwd, body } = context;

        const runCommands = async (
          response: SCHEMA.AResponseForStartRequest
        ) => {
          const starterCommands = response?.starter?.commands;
          if (starterCommands) {
            for (const cmd of starterCommands) {
              await commands.execute(cmd.id, cmd.args);
            }
          } else if (response.status === 'done' && response.path.length) {
            await commands.execute('filebrowser:open-path', {
              path: response.path,
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
            )) as SCHEMA.AResponseForStartRequest;
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
                  cwd: response.path,
                };
                await runCommands(response);
                content.model.status = 'ready';
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
      icon: (args: any) => {
        const context = (args as any) as IStartContext;
        return manager.icon(context.name, context.starter);
      },
    });

    let metadata: NotebookMetadata | null;

    const onCurrentNotebook = () => {
      const { currentWidget } = notebooks;
      if (!currentWidget) {
        if (metadata) {
          metadata.dispose();
        }
        metadata = null;
        notebooks.currentChanged.disconnect(onCurrentNotebook);
      } else if (metadata != null) {
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
      iconClass: DEFAULT_ICON_CLASS,
    });

    const starterPattern = new RegExp(`[\?&]starter=(.+?)(/.*)`);

    commands.addCommand(CommandIDs.routerStart, {
      execute: async (args) => {
        console.log('routing', args);
        const loc = args as IRouter.ILocation;
        const starterMatch = loc.request.match(starterPattern);
        if (starterMatch == null) {
          return;
        }
        const [name, cwd] = starterMatch.slice(1);

        await manager.ready;

        const starter = manager.starters[name];

        if (starter == null) {
          return;
        }

        const url = URLExt.join(PageConfig.getOption('treeUrl'), cwd);

        console.log('navigating to', url);

        router.navigate(url);

        void commands.execute(CommandIDs.start, {
          name,
          cwd,
          starter,
        });

        if (starter.schema) {
          let notHiddenCount = 0;
          let retries = 20;
          const contentId = `id-jp-starters-${name}`;

          const expandInterval = setInterval(() => {
            if (retries-- <= 0) {
              clearInterval(expandInterval);
            }
            const hidden = document.querySelector(
              `#jp-right-stack.${CSS.P.hidden}`
            );
            if (hidden) {
              shell.expandRight();
              shell.activateById(contentId);
              return;
            }
            const sidebar = document.querySelector(
              `.${CSS.BUILDER}:not(.${CSS.P.hidden})`
            );
            if (sidebar) {
              notHiddenCount++;
              shell.expandRight();
              shell.activateById(contentId);
              if (notHiddenCount > 3) {
                clearInterval(expandInterval);
              }
            }
          }, 500);
        }

        return router.stop;
      },
    });

    router.register({
      command: CommandIDs.routerStart,
      pattern: starterPattern,
      rank: 29,
    });

    const notebookbutton = new NotebookStarter({ commands });

    app.docRegistry.addWidgetExtension('Notebook', notebookbutton);

    const cardsAdded = [] as string[];

    manager.changed.connect(() => {
      const { starters } = manager;
      for (const name in starters) {
        if (cardsAdded.indexOf(name) !== -1) {
          continue;
        }
        launcher.add({
          command: CommandIDs.start,
          args: { name, starter: starters[name] },
          category: CATEGORY,
        });
        cardsAdded.push(name);
      }
    });

    manager.fetch().catch(console.warn);
  },
};

export default plugin;
