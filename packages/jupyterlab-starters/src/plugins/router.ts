import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
  ILabShell,
  IRouter,
} from '@jupyterlab/application';
import { URLExt, PageConfig } from '@jupyterlab/coreutils';

import { CSS } from '../css';
import {
  CommandIDs,
  IStarterManager,
  PKG,
  STARTER_PATTERN,
  STARTER_SEARCH_PARAM,
  EMOJI,
} from '../tokens';

export const routerPlugin: JupyterFrontEndPlugin<void> = {
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
