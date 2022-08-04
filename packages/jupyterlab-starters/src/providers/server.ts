import { ServerConnection } from '@jupyterlab/services';
import { PromiseDelegate } from '@lumino/coreutils';
import { Signal } from '@lumino/signaling';

import * as SCHEMA from '../_schema';
import { IStarterProvider, API } from '../tokens';

const { makeRequest, makeSettings } = ServerConnection;

/** Discovers starters from the server. */
export class ServerStarterProvider implements IStarterProvider {
  private _starters: SCHEMA.NamedStarters = {};
  private _changed: Signal<IStarterProvider, void>;
  private _ready = new PromiseDelegate<void>();

  private _serverSettings = makeSettings();

  constructor() {
    this._changed = new Signal<IStarterProvider, void>(this);
  }

  async fetch(): Promise<void> {
    const response = await makeRequest(API, {}, this._serverSettings);
    const content = (await response.json()) as SCHEMA.AResponseForAnStartersRequest;
    this._starters = content.starters;
    this._changed.emit(void 0);
    this._ready.resolve(void 0);
  }

  get starters(): SCHEMA.NamedStarters {
    return { ...this._starters };
  }

  starter(name: string): SCHEMA.Starter {
    return this._starters[name];
  }

  get ready(): Promise<void> {
    return this._ready.promise;
  }
}
