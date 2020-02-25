import {
  NS,
  FACTORY,
  IJSONSchemaFormTracker,
  FILE_TYPE,
  CommandIds,
  ICON_NAME,
  ICON_SVG,
  ICON_CLASS
} from './tokens';

import {
  ILayoutRestorer,
  ILabShell,
  JupyterLab,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ICommandPalette, WidgetTracker } from '@jupyterlab/apputils';
import { IRenderMimeRegistry } from '@jupyterlab/rendermime';

import { IFileBrowserFactory } from '@jupyterlab/filebrowser';

import { IDocumentManager } from '@jupyterlab/docmanager';

import { IIconRegistry } from '@jupyterlab/ui-components';

import { JSONSchemaFormDocument, JSONSchemaFormFactory } from './document';
import { SchemaManager } from './manager';

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
    IDocumentManager,
    ILabShell,
    IRenderMimeRegistry
  ],
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
  shell: ILabShell,
  rendermime: IRenderMimeRegistry
): IJSONSchemaFormTracker {
  icons.addIcon({
    name: ICON_NAME,
    svg: ICON_SVG
  });

  const schemaManager = new SchemaManager({ shell, rendermime });

  const factory = new JSONSchemaFormFactory({
    name: FACTORY,
    docManager,
    fileTypes: ['json'],
    schemaManager
  });

  const { commands } = app;
  const tracker = new WidgetTracker<JSONSchemaFormDocument>({ namespace: NS });

  // Handle state restoration.
  restorer
    .restore(tracker, {
      command: 'docmanager:open',
      args: widget => ({ path: widget.context.path, factory: FACTORY }),
      name: widget => widget.context.path
    })
    .catch(console.warn);

  factory.widgetCreated.connect(async (sender, widget) => {
    widget.title.iconClass = ICON_CLASS;

    // Notify the instance tracker if restore data needs to update.
    widget.context.pathChanged.connect(async () => {
      await tracker.save(widget);
    });
    await tracker.add(widget);
  });
  app.docRegistry.addWidgetFactory(factory);

  // register the filetype
  app.docRegistry.addFileType(FILE_TYPE);

  // Add a command for creating a new JSON form file.
  commands.addCommand(CommandIds.createNew, {
    label: FILE_TYPE.displayName,
    iconClass: ICON_CLASS,
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

  return tracker;
}
