import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
  ILabShell,
  IRouter,
} from '@jupyterlab/application';
import { URLExt, PageConfig } from '@jupyterlab/coreutils';
import mergeWith from 'lodash.mergewith';

import { CSS } from '../css';
import {
  CommandIDs,
  EMOJI,
  IStartContext,
  IStarterManager,
  PKG,
  STARTER_BODY_PARAM,
  STARTER_NAME_PARAM,
  STARTER_NOUI_PARAM,
  STARTER_PATTERN,
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
        const parsedUrl = new URL(`${window.location.origin}/${loc.request}`);

        const starterPath = parsedUrl.searchParams.get(STARTER_NAME_PARAM);

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
        let body = null;
        const rawBody = parsedUrl.searchParams.get(STARTER_BODY_PARAM);

        if (rawBody) {
          try {
            body = JSON.parse(rawBody);
          } catch (err) {
            console.warn(EMOJI, `Couldn't parse body: ${err}`);
          }
        }

        if (starter.schema?.default) {
          body = mergeWith(starter.schema.default, body || {});
        }

        let noUI = false;
        let rawNoUI = parsedUrl.searchParams.get(STARTER_NOUI_PARAM);

        if (rawNoUI != null) {
          try {
            noUI = !!JSON.parse(rawNoUI);
          } catch (err) {
            console.warn(EMOJI, `Couldn't parse UI: ${err}`);
          }
        }

        console.info(
          EMOJI,
          'Starting',
          name,
          'in',
          url,
          noUI ? 'without UI' : 'with UI',
          body
        );

        router.navigate(url);

        const startArgs: Partial<IStartContext> = {
          name,
          cwd,
          starter,
          noUI,
          ...(body ? { body } : {}),
        };

        let isComplete = false;
        commands
          .execute(CommandIDs.start, startArgs)
          .then((response) => {
            isComplete = true;
          })
          .catch(console.warn);

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
            const sidebar = document.querySelector(`.${CSS.BUILDER}`);
            if (sidebar) {
              notHiddenCount++;
              shell.expandRight();
              shell.activateById(contentId);
              if (notHiddenCount > 3 || !sidebar.classList.contains(CSS.P.hidden)) {
                clearInterval(expandInterval);
              }
            } else if (isComplete) {
              clearInterval(expandInterval);
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
