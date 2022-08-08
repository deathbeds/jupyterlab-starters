import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
  ILabShell,
  IRouter,
} from '@jupyterlab/application';
import { URLExt, PageConfig } from '@jupyterlab/coreutils';
import { ILauncher } from '@jupyterlab/launcher';
import { NotebookPanel, INotebookTracker } from '@jupyterlab/notebook';
import { IRenderMimeRegistry } from '@jupyterlab/rendermime';
import { IRunningSessionManagers } from '@jupyterlab/running';
import { ISettingRegistry } from '@jupyterlab/settingregistry';

import '../style/index.css';

import * as SCHEMA from './_schema';
import { CSS } from './css';
import { StarterManager } from './manager';
import { NotebookStarter } from './notebookbutton';
import { ServerStarterProvider } from './providers/server';
import { SettingsProvider } from './providers/settings';
import { BrowserStarterRunner } from './runners/browser';
import { ServerStarterRunner } from './runners/server';
import {
  CommandIDs,
  CATEGORY,
  IStartContext,
  IStarterManager,
  DEFAULT_ICON_CLASS,
  CORE_PLUGIN_ID,
  SETTINGS_PLUGIN_ID,
  PKG,
  SETTINGS_NAME,
  SERVER_NAME,
  STARTER_PATTERN,
  STARTER_SEARCH_PARAM,
  EMOJI,
} from './tokens';
import { BodyBuilder } from './widgets/builder';
import { NotebookMetadata } from './widgets/meta';

const corePlugin: JupyterFrontEndPlugin<IStarterManager> = {
  id: CORE_PLUGIN_ID,
  requires: [
    JupyterFrontEnd.IPaths,
    ILabShell,
    ILauncher,
    INotebookTracker,
    IRenderMimeRegistry,
    IRunningSessionManagers,
  ],
  autoStart: true,
  provides: IStarterManager,
  activate: (
    app: JupyterFrontEnd,
    paths: JupyterFrontEnd.IPaths,
    shell: ILabShell,
    launcher: ILauncher,
    notebooks: INotebookTracker,
    rendermime: IRenderMimeRegistry,
    running: IRunningSessionManagers
  ): IStarterManager => {
    const { commands } = app;
    const manager: IStarterManager = new StarterManager({ rendermime });

    running.add(manager);

    commands.addCommand(CommandIDs.start, {
      execute: async (args: any) => {
        const context = args as any as IStartContext;
        const { starter, name, cwd, body } = context;

        const runCommands = async (response: SCHEMA.AResponseForStartRequest) => {
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
                console.error(EMOJI, `Unknown status ${response.status}`, response);
            }
          });
        } else if (starter.schema && body) {
          return await manager.start(name, starter, cwd, body);
        } else {
          const response = await manager.start(name, starter, cwd, body);
          if (response) {
            await runCommands(response);
          }
        }
      },
      label: (args: any) => args.starter.label,
      caption: (args: any) => args.starter.description,
      icon: (args: any) => {
        const context = args as any as IStartContext;
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
        return `Configure ${notebook.title.label.replace(/.ipynb$/, '')} as Starter`;
      },
      iconClass: DEFAULT_ICON_CLASS,
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
          category: starters[name].category || CATEGORY,
          ...(starters[name].rank == null ? {} : { rank: starters[name].rank }),
        });
        cardsAdded.push(name);
      }
    });

    manager.fetch().catch(console.warn);

    return manager;
  },
};

const serverProviderPlugin: JupyterFrontEndPlugin<void> = {
  id: `${PKG.name}:server-provider`,
  requires: [IStarterManager],
  autoStart: true,
  activate: (app: JupyterFrontEnd, manager: IStarterManager) => {
    const provider = new ServerStarterProvider();
    manager.addProvider(SERVER_NAME, provider);
  },
};

const serverRunnerPlugin: JupyterFrontEndPlugin<void> = {
  id: `${PKG.name}:server-runner`,
  requires: [IStarterManager],
  autoStart: true,
  activate: (app: JupyterFrontEnd, manager: IStarterManager) => {
    const runner = new ServerStarterRunner({ manager });
    manager.addRunner(SERVER_NAME, runner);
  },
};

const settingsProviderPlugin: JupyterFrontEndPlugin<void> = {
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

const browserRunnerPlugin: JupyterFrontEndPlugin<void> = {
  id: `${PKG.name}:browser-runner`,
  requires: [IStarterManager],
  autoStart: true,
  activate: (app: JupyterFrontEnd, manager: IStarterManager) => {
    const { contents } = app.serviceManager;
    const runner = new BrowserStarterRunner({ manager, contents });
    manager.addRunner('browser', runner);
  },
};

const routerPlugin: JupyterFrontEndPlugin<void> = {
  id: `${PKG.name}:router`,
  requires: [ILabShell, IRouter, IStarterManager],
  autoStart: true,
  activate: (
    app: JupyterFrontEnd,
    shell: ILabShell,
    router: IRouter,
    manager: IStarterManager
  ) => {
    const starterPattern = STARTER_PATTERN;
    const { commands } = app;

    commands.addCommand(CommandIDs.routerStart, {
      execute: async (args) => {
        const loc = args as IRouter.ILocation;
        const parsedUrl = new URL(`http://127.0.0.1/${loc.request}`);

        const starterPath = parsedUrl.searchParams.get(STARTER_SEARCH_PARAM);

        if (starterPath == null) {
          return;
        }

        const parts = starterPath.split('/', 2);

        let cwd = '';
        const name = parts[0];

        if (parts.length == 2) {
          cwd = parts[1];
        }

        await manager.fetch();

        const starter = manager.starters[name];

        if (starter == null) {
          console.warn(
            EMOJI,
            'Starter',
            name,
            'not one of',
            Object.keys(manager.starters),
            '., not starting.'
          );
          return;
        }

        const url = URLExt.join(PageConfig.getOption('appUrl'), '/tree/', cwd);

        console.info(EMOJI, 'Starting', name, 'in', url);

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
            if (shell.rightCollapsed) {
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
  },
};

const plugins = [
  corePlugin,
  serverProviderPlugin,
  serverRunnerPlugin,
  settingsProviderPlugin,
  browserRunnerPlugin,
  routerPlugin,
];

export default plugins;
