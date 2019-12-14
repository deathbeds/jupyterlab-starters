import { URLExt } from '@jupyterlab/coreutils';
import { Signal } from '@phosphor/signaling';
import { ServerConnection } from '@jupyterlab/services';
import { IStarterManager, IStarters } from './tokens';

import { API } from './tokens';

export class StarterManager implements IStarterManager {
  private _changed: Signal<IStarterManager, void>;
  private _starters: IStarters = {};
  private _serverSettings = ServerConnection.makeSettings();

  constructor() {
    this._changed = new Signal<IStarterManager, void>(this);
  }

  get changed() {
    return this._changed;
  }

  get starters(): IStarters {
    return { ...this._starters };
  }

  starter(name: string) {
    return this._starters[name];
  }

  async fetch() {
    const response = await ServerConnection.makeRequest(
      API,
      {},
      this._serverSettings
    );
    this._starters = (await response.json())['starters'] as IStarters;
    this._changed.emit(void 0);
  }

  async copy(name: string, contentsPath: string) {
    const response = await ServerConnection.makeRequest(
      URLExt.join(API, name, contentsPath),
      {
        method: 'POST'
      },
      this._serverSettings
    );
    const result = await response.json();
    console.log(result);
  }
}
