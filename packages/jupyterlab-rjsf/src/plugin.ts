import {
  NS,
  FACTORY,
  IJSONSchemaFormTracker,
  FILE_TYPES,
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

import { JSONMatcher } from './matchers/json';
import { YAMLMatcher } from './matchers/yaml';

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
  const jsonMatcher = new JSONMatcher();
  const yamlMatcher = new YAMLMatcher();

  for (const matcher of [jsonMatcher, yamlMatcher]) {
    schemaManager.registerReader(matcher);
    schemaManager.registerWriter(matcher);
  }

  const factory = new JSONSchemaFormFactory({
    name: FACTORY,
    docManager,
    fileTypes: Object.keys(FILE_TYPES).map((key) => FILE_TYPES[key].name),
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

  for (const fileType in FILE_TYPES) {
    // register the filetype
    app.docRegistry.addFileType(FILE_TYPES[fileType]);

    // Add a command for creating a new Form Instance file.
    commands.addCommand(`${CommandIds.createNew}-${fileType}`, {
      label: FILE_TYPES[fileType].displayName,
      iconClass: ICON_CLASS,
      caption: `Create a new JSON Schema Form ${FILE_TYPES[fileType].displayName}`,
      execute: async () => {
        let path = browserFactory.defaultBrowser.model.path;
        const model = await commands.execute('docmanager:new-untitled', {
          path,
          type: 'file',
          ext: FILE_TYPES[fileType].extensions[0]
        });
        return await commands.execute('docmanager:open', {
          path: model.path,
          factory: FACTORY
        });
      }
    });
  }

  return tracker;
}

export default [plugin];
