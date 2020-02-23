import {
  NS,
  FACTORY,
  IJSONSchemaFormTracker,
  FILE_TYPE,
  ICON,
  CommandIds,
  ICON_NAME,
  ICON_SVG
} from './tokens';

import {
  ILayoutRestorer,
  JupyterLab,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ICommandPalette, WidgetTracker } from '@jupyterlab/apputils';

import { IFileBrowserFactory } from '@jupyterlab/filebrowser';

import { ILauncher } from '@jupyterlab/launcher';

import {IDocumentManager} from '@jupyterlab/docmanager';

import { IIconRegistry } from '@jupyterlab/ui-components';

import { JSONSchemaFormDocument, JSONSchemaFormFactory } from './factory';

/**
 * The editor tracker extension.
 */
const plugin: JupyterFrontEndPlugin<IJSONSchemaFormTracker> = {
  activate,
  id: `${NS}:plugin`,
  requires: [
    IFileBrowserFactory,
    ILayoutRestorer,
    ICommandPalette,
    IIconRegistry,
    IDocumentManager
  ],
  optional: [ILauncher],
  provides: IJSONSchemaFormTracker,
  autoStart: true
};

export default plugin;

function activate(
  app: JupyterLab,
  browserFactory: IFileBrowserFactory,
  restorer: ILayoutRestorer,
  palette: ICommandPalette,
  icons: IIconRegistry,
  docManager: IDocumentManager,
  launcher: ILauncher | null
): IJSONSchemaFormTracker {
  icons.addIcon({
    name: ICON_NAME,
    svg: ICON_SVG
  });

  const factory = new JSONSchemaFormFactory({
    name: FACTORY,
    docManager,
    fileTypes: ['json']
  });
  const { commands } = app;
  const tracker = new WidgetTracker<JSONSchemaFormDocument>({ namespace: NS });

  // Handle state restoration.
  restorer.restore(tracker, {
    command: 'docmanager:open',
    args: widget => ({ path: widget.context.path, factory: FACTORY }),
    name: widget => widget.context.path
  });

  factory.widgetCreated.connect((sender, widget) => {
    widget.title.icon = `jp-MaterialIcon ${ICON}`; // TODO change

    // Notify the instance tracker if restore data needs to update.
    widget.context.pathChanged.connect(() => {
      tracker.save(widget);
    });
    tracker.add(widget);
  });
  app.docRegistry.addWidgetFactory(factory);

  // register the filetype
  app.docRegistry.addFileType(FILE_TYPE);

  // Add a command for creating a new JSON form file.
  commands.addCommand(CommandIds.createNew, {
    label: FILE_TYPE.displayName,
    iconClass: `jp-MaterialIcon ${ICON}`,
    caption: 'Create a new JSON Form',
    execute: async () => {
      let path = browserFactory.defaultBrowser.model.path;
      const model = await commands.execute('docmanager:new-untitled', {
        path,
        type: 'file',
        ext: '.json'
      });
      return commands.execute('docmanager:open', {
        path: model.path,
        factory: FACTORY
      });
    }
  });

  // Add a launcher item if the launcher is available.
  if (launcher) {
    launcher.add({
      command: CommandIds.createNew,
      rank: 1,
      category: 'Other'
    });
  }

  return tracker;
}
