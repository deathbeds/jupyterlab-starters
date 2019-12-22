import { IDisposable, DisposableDelegate } from '@phosphor/disposable';

import { CommandRegistry } from '@phosphor/commands';

import { CommandToolbarButton } from '@jupyterlab/apputils';

import { NotebookPanel, INotebookModel } from '@jupyterlab/notebook';

import { DocumentRegistry } from '@jupyterlab/docregistry';

import { CommandIDs } from './tokens';

export class NotebookStarter
  implements DocumentRegistry.IWidgetExtension<NotebookPanel, INotebookModel> {
  private _commands: CommandRegistry;

  constructor(options: NotebookStarter.IOptions) {
    this._commands = options.commands;
  }

  createNew(
    panel: NotebookPanel,
    _context: DocumentRegistry.IContext<INotebookModel>
  ): IDisposable {
    let button = new CommandToolbarButton({
      commands: this._commands,
      id: CommandIDs.notebookMeta
    });

    panel.toolbar.insertItem(10, 'starter-notebook', button);

    return new DisposableDelegate(() => button.dispose());
  }
}

export namespace NotebookStarter {
  export interface IOptions {
    commands: CommandRegistry;
  }
}
